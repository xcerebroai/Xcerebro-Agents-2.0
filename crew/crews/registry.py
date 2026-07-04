"""
Xcerebro 2.0 — Crew Registry

Loads agent and crew definitions from YAML files in /agents/.
Provides the orchestration interface for the FastAPI runtime.
"""

from pathlib import Path
from typing import Any, Optional
import yaml
from loguru import logger

from crewai import Agent, Crew, Task, Process, LLM

from config import settings
from tools.ghl import get_ghl_tools
from tools.sync_log import get_sync_log_tools
from routing.router import (
    ModelRouter,
    TaskContext,
    load_policy_from_yaml,
    to_openrouter_slug,
    cost_for_slug,
)


MODEL_ALIASES = {
    "claude-sonnet-4-5": "anthropic/claude-sonnet-4.5",
    "claude-haiku-4-5": "anthropic/claude-haiku-4.5",
    "claude-opus-4-1": "anthropic/claude-opus-4.5",
    "claude-sonnet-4": "anthropic/claude-sonnet-latest",
    "claude-opus-4": "anthropic/claude-opus-4.5",
}

# Maps YAML can_call_tools prefixes to tool loader functions.
# Add new tool families here as they are implemented.
TOOL_LOADERS = {
    "ghl.": get_ghl_tools,
    "sync_log.": get_sync_log_tools,
}

# Maps outbound action types to the declared tool names that imply them.
# Order = severity: the FIRST matching type classifies the invocation,
# so a payment-capable agent is gated as "payment" even if it can also email.
ACTION_TYPE_TOOLS: dict[str, tuple[str, ...]] = {
    "payment": ("stripe.create_invoice", "stripe.charge", "stripe.create_charge"),
    "refund": ("stripe.refund", "stripe.create_refund"),
    "public_post": ("postiz.schedule_post", "postiz.publish"),
    "email": ("email.send", "gmail.send"),
    "dm": ("sms.send", "instagram.send_dm", "ig.send_dm"),
    "crm_update": ("ghl.update_contact", "ghl.add_tag", "ghl.merge_duplicates", "ghl.create_contact"),
    "calendar_booking": ("calendar.create_event", "calendar.update_event"),
}


class CrewRegistry:
    """Loads + indexes all agent and crew definitions."""

    def __init__(self, agents_path: Path):
        self.agents_path = Path(agents_path)
        self.agents: dict[str, dict] = {}
        self.crews: dict[str, dict] = {}
        self.workflow_map: dict[str, str] = {}
        self._memory = None  # MemoryManager, initialized lazily
        self._governance = None  # GovernanceStore, injected by main.py at startup
        self._router = ModelRouter()

    def set_governance(self, store) -> None:
        """Inject the shared GovernanceStore (approvals, trust, spend)."""
        self._governance = store

    # ── memory ────────────────────────────────────────────────────────────────

    def _get_memory(self):
        """Lazy-init MemoryManager so import errors don't crash startup."""
        if self._memory is None and settings.database_url:
            try:
                from tools.memory import MemoryManager
                self._memory = MemoryManager(
                    database_url=settings.database_url,
                    openrouter_api_key=getattr(settings, "openrouter_api_key", ""),
                )
            except Exception as e:
                logger.warning(f"MemoryManager init failed (degraded): {e}")
        return self._memory

    # ── loading ───────────────────────────────────────────────────────────────

    def load_all(self) -> None:
        if not self.agents_path.exists():
            logger.warning(f"Agents path {self.agents_path} not found")
            return

        for yaml_file in (self.agents_path / "tier-a").glob("*.yaml"):
            self._load_agent_file(yaml_file, tier="a")
        for yaml_file in (self.agents_path / "tier-b").glob("*.yaml"):
            self._load_agent_file(yaml_file, tier="b")

        crews_dir = self.agents_path.parent / "crews"
        if crews_dir.exists():
            for yaml_file in crews_dir.glob("*.yaml"):
                self._load_crew_file(yaml_file)

        logger.info(f"Registry loaded: {len(self.agents)} agents, {len(self.crews)} crews")

    def _load_agent_file(self, path: Path, tier: str) -> None:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            agent_id = data.get("id") or path.stem
            data["_tier"] = tier
            data["_path"] = str(path)
            self.agents[agent_id] = data
        except Exception as e:
            logger.error(f"Failed to load agent {path}: {e}")

    def _load_crew_file(self, path: Path) -> None:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            crew_id = data.get("id") or path.stem
            self.crews[crew_id] = data
            for workflow in data.get("triggers_for_workflows", []):
                self.workflow_map[workflow] = crew_id
        except Exception as e:
            logger.error(f"Failed to load crew {path}: {e}")

    # ── lookups ───────────────────────────────────────────────────────────────

    def get_agent(self, agent_id: str) -> Optional[dict]:
        return self.agents.get(agent_id)

    def get_crew(self, crew_id: str) -> Optional[dict]:
        return self.crews.get(crew_id)

    def workflow_to_crew(self, workflow_name: str) -> Optional[str]:
        return self.workflow_map.get(workflow_name)

    def list_tier(self, tier: str) -> list[dict]:
        return [
            {"id": aid, "name": a.get("name"), "role": a.get("role")}
            for aid, a in self.agents.items()
            if a.get("_tier") == tier
        ]

    def list_crews(self) -> list[dict]:
        return [
            {"id": cid, "name": c.get("name"), "description": c.get("description")}
            for cid, c in self.crews.items()
        ]

    # ── tool wiring ───────────────────────────────────────────────────────────

    def _build_tools(self, agent_def: dict) -> list:
        """Instantiate tools declared in can_call_tools."""
        tool_names: list[str] = agent_def.get("permissions", {}).get("can_call_tools", [])
        if not tool_names:
            return []

        # Group by prefix so each loader gets all its tool names at once
        by_prefix: dict[str, list[str]] = {}
        for name in tool_names:
            for prefix, loader in TOOL_LOADERS.items():
                if name.startswith(prefix):
                    by_prefix.setdefault(prefix, []).append(name)
                    break

        tools = []
        for prefix, names in by_prefix.items():
            loader = TOOL_LOADERS[prefix]
            tools.extend(loader(names))

        if tools:
            logger.debug(f"Wired {len(tools)} tool(s): {[t.name for t in tools]}")
        return tools

    # ── approval ──────────────────────────────────────────────────────────────

    def classify_action_type(self, agent_id: str) -> Optional[str]:
        """Highest-severity outbound action type this agent's declared tools imply."""
        agent_def = self.agents.get(agent_id) or {}
        declared = set(agent_def.get("permissions", {}).get("can_call_tools", []))
        for action_type, tool_names in ACTION_TYPE_TOOLS.items():
            if declared.intersection(tool_names):
                return action_type
        return None

    def requires_approval(self, agent_id: str, task: str) -> tuple[bool, Optional[str]]:
        """
        Decide whether an invocation needs a human approval gate.

        Returns (needs_approval, action_type). Graduated autonomy: an earned,
        human-flipped auto_approve for this (agent, action_type) skips the gate
        even for always_require_approval agents — earning trust is the point.
        """
        agent_def = self.agents.get(agent_id) or {}
        perms = agent_def.get("permissions", {})
        action_type = self.classify_action_type(agent_id)

        if action_type and self._governance and self._governance.is_auto_approved(agent_id, action_type):
            return False, action_type

        if perms.get("always_require_approval"):
            return True, action_type or "general"

        if action_type and getattr(settings, f"approval_required_for_{action_type}", False):
            return True, action_type

        return False, action_type

    # ── limits (spend cap + rate limit) ───────────────────────────────────────

    def check_limits(self) -> None:
        """Raise RuntimeError before any LLM work if daily spend cap or hourly rate is hit."""
        gov = self._governance
        if not gov:
            return
        cap = settings.max_daily_llm_spend_usd
        if cap:
            spent = gov.today_spend()
            if spent >= cap:
                raise RuntimeError(
                    f"SPEND_CAP: daily LLM spend ${spent:.2f} >= ${cap:.2f} cap — task refused"
                )
        if settings.max_tasks_per_hour and gov.calls_last_hour() >= settings.max_tasks_per_hour:
            raise RuntimeError(
                f"RATE_LIMIT: {settings.max_tasks_per_hour} tasks/hour reached — task refused"
            )

    def _log_usage(self, agent_id: str, model_slug: str, crew: "Crew") -> None:
        """Persist token usage + estimated cost from a finished single-agent run."""
        gov = self._governance
        if not gov:
            return
        usage = getattr(crew, "usage_metrics", None)
        if not usage:
            return
        tin = getattr(usage, "prompt_tokens", 0) or 0
        tout = getattr(usage, "completion_tokens", 0) or 0
        gov.log_llm_call(
            agent_id=agent_id,
            model_slug=model_slug,
            input_tokens=tin,
            output_tokens=tout,
            cost_usd=cost_for_slug(model_slug, tin, tout),
        )

    def _log_crew_usage(self, crew_id: str, member_models: list[tuple[str, str]], crew: "Crew") -> None:
        """
        Persist token usage + cost for a multi-agent crew run.

        CrewAI's Crew.usage_metrics is a single aggregate across every member's
        LLM calls — it doesn't break tokens down per agent/model. Splitting it
        evenly across members isn't exact (a verbose premium-tier agent likely
        used more of the tokens than a terse economy-tier one), but it fixes the
        real bug: previously ALL cost was attributed to the LAST member's model,
        so a crew with one premium (Opus) agent and three cheap ones logged as
        if 100% of spend was the cheap model. Even split means both the total
        (what the kill switch checks) and the by-model breakdown reflect every
        model actually used, not just the last one.
        # ponytail: even split, not true per-agent attribution — upgrade path is
        # a CrewAI task_callback capturing each task's own token usage, if the
        # installed CrewAI version exposes it.
        """
        gov = self._governance
        if not gov or not member_models:
            return
        usage = getattr(crew, "usage_metrics", None)
        if not usage:
            return
        total_in = getattr(usage, "prompt_tokens", 0) or 0
        total_out = getattr(usage, "completion_tokens", 0) or 0
        n = len(member_models)
        share_in, share_out = total_in // n, total_out // n
        for i, (member_agent_id, model_slug) in enumerate(member_models):
            # remainder from integer division goes to the first member
            tin = share_in + (total_in % n if i == 0 else 0)
            tout = share_out + (total_out % n if i == 0 else 0)
            gov.log_llm_call(
                agent_id=f"{crew_id}:{member_agent_id}",
                model_slug=model_slug,
                input_tokens=tin,
                output_tokens=tout,
                cost_usd=cost_for_slug(model_slug, tin, tout),
            )

    # ── agent invocation ──────────────────────────────────────────────────────

    async def invoke(self, agent_id: str, task: str, context: dict) -> Any:
        agent_def = self.agents.get(agent_id)
        if not agent_def:
            raise ValueError(f"Agent {agent_id} not found")

        self.check_limits()
        llm, model_slug = self._build_llm(agent_def, task=task)
        tools = self._build_tools(agent_def)

        # Inject relevant past memories into the task description
        memory_context = ""
        mem = self._get_memory()
        if mem:
            memories = mem.retrieve(agent_id=agent_id, query=task, top_k=5)
            memory_context = mem.format_for_context(memories)

        full_task = f"{task}\n\n{memory_context}".strip() if memory_context else task

        cw_agent = Agent(
            role=agent_def.get("role", agent_id),
            goal=agent_def.get("goal", "Complete the assigned task"),
            backstory=agent_def.get("backstory", ""),
            llm=llm,
            tools=tools,
            function_calling_llm=llm,  # use Claude's native tool-call API, not ReAct text format
            verbose=True,
            allow_delegation=False,
        )

        cw_task = Task(
            description=full_task,
            expected_output=agent_def.get("expected_output", "A clear, actionable response"),
            agent=cw_agent,
        )

        crew = Crew(
            agents=[cw_agent],
            tasks=[cw_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff(inputs=context)
        result_str = str(result)

        self._log_usage(agent_id, model_slug, crew)

        # Store this invocation as a memory for future runs
        if mem:
            summary = f"Task: {task[:200]}\nResult: {result_str[:600]}"
            mem.store(
                agent_id=agent_id,
                content=summary,
                memory_type="episodic",
                metadata={"context_keys": list(context.keys())},
            )

        return result_str

    async def run_crew(self, crew_id: str, inputs: dict) -> Any:
        crew_def = self.crews.get(crew_id)
        if not crew_def:
            raise ValueError(f"Crew {crew_id} not found")

        self.check_limits()

        agents = []
        tasks = []
        agent_lookup = {}
        member_models: list[tuple[str, str]] = []  # (agent_id, model_slug) per member that actually ran

        # Map each member to their task text so routing can see it (keyword escalation)
        task_by_agent = {
            t.get("agent_id"): t.get("description", "")
            for t in crew_def.get("tasks", [])
        }

        for member in crew_def.get("members", []):
            agent_def = self.agents.get(member["agent_id"])
            if not agent_def:
                logger.warning(f"Agent {member['agent_id']} not found, skipping")
                continue
            llm, member_model_slug = self._build_llm(
                agent_def, task=task_by_agent.get(member["agent_id"], "")
            )
            member_models.append((member["agent_id"], member_model_slug))
            tools = self._build_tools(agent_def)
            cw_agent = Agent(
                role=agent_def.get("role", member["agent_id"]),
                goal=agent_def.get("goal", "Complete the assigned task"),
                backstory=agent_def.get("backstory", ""),
                llm=llm,
                tools=tools,
                verbose=True,
                allow_delegation=member.get("can_delegate", False),
            )
            agents.append(cw_agent)
            agent_lookup[member["agent_id"]] = cw_agent

        for task_def in crew_def.get("tasks", []):
            assigned_agent = agent_lookup.get(task_def.get("agent_id"))
            if not assigned_agent and agents:
                assigned_agent = agents[0]
            cw_task = Task(
                description=task_def["description"],
                expected_output=task_def.get("expected_output", "Complete result"),
                agent=assigned_agent,
            )
            tasks.append(cw_task)

        if crew_def.get("hierarchical"):
            manager_llm, _ = self._build_llm({})
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,
                manager_llm=manager_llm,
                verbose=True,
            )
        else:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
            )

        result = crew.kickoff(inputs=inputs)
        self._log_crew_usage(crew_id, member_models, crew)
        return str(result)

    async def resume_after_approval(self, approval_record: dict) -> Any:
        return await self.invoke(
            agent_id=approval_record["agent_id"],
            task=approval_record["task"],
            context=approval_record.get("context", {}),
        )

    # ── LLM builder ───────────────────────────────────────────────────────────

    def _build_llm(self, agent_def: dict, task: str = "") -> tuple[LLM, str]:
        """
        Build the LLM for an agent. Returns (llm, openrouter_slug).

        When routing is enabled, the ModelRouter picks the tier model
        (economy/balanced/premium per agent YAML `model_routing`, with keyword
        escalation on the task text). Execution ALWAYS goes through OpenRouter —
        routing only changes which slug we ask it for.
        """
        if settings.routing_enabled and agent_def:
            policy = load_policy_from_yaml(agent_def)
            decision = self._router.route(policy, TaskContext(
                agent_id=agent_def.get("id", "unknown"),
                task_description=task or "",
            ))
            model = to_openrouter_slug(decision.model_id)
            logger.info(
                f"[routing] {agent_def.get('id', '?')} -> {model} ({decision.reason})"
            )
        else:
            model = agent_def.get("llm_model", settings.default_llm_model)
            if model in MODEL_ALIASES:
                model = MODEL_ALIASES[model]
            if model:
                model = model.replace("openrouter/", "")

        import os
        api_key = getattr(settings, "openrouter_api_key", None) or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENROUTER_API_KEY in Railway variables.")

        return LLM(model=f"openrouter/{model}", api_key=api_key), model
