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
}


class CrewRegistry:
    """Loads + indexes all agent and crew definitions."""

    def __init__(self, agents_path: Path):
        self.agents_path = Path(agents_path)
        self.agents: dict[str, dict] = {}
        self.crews: dict[str, dict] = {}
        self.workflow_map: dict[str, str] = {}
        self._memory = None  # MemoryManager, initialized lazily

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
        tool_names: list[str] = agent_def.get("can_call_tools", [])
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

    def requires_approval(self, agent_id: str, task: str) -> bool:
        # ponytail: approval disabled until /slack/interactions endpoint exists
        return False

    # ── agent invocation ──────────────────────────────────────────────────────

    async def invoke(self, agent_id: str, task: str, context: dict) -> Any:
        agent_def = self.agents.get(agent_id)
        if not agent_def:
            raise ValueError(f"Agent {agent_id} not found")

        llm = self._build_llm(agent_def)
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
            memory=True,
            verbose=True,
        )

        result = crew.kickoff(inputs=context)
        result_str = str(result)

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

        agents = []
        tasks = []
        agent_lookup = {}

        for member in crew_def.get("members", []):
            agent_def = self.agents.get(member["agent_id"])
            if not agent_def:
                logger.warning(f"Agent {member['agent_id']} not found, skipping")
                continue
            llm = self._build_llm(agent_def)
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
            manager_llm = self._build_llm({})
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,
                manager_llm=manager_llm,
                memory=True,
                verbose=True,
            )
        else:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                memory=True,
                verbose=True,
            )

        result = crew.kickoff(inputs=inputs)
        return str(result)

    async def resume_after_approval(self, approval_record: dict) -> Any:
        return await self.invoke(
            agent_id=approval_record["agent_id"],
            task=approval_record["task"],
            context=approval_record.get("context", {}),
        )

    # ── LLM builder ───────────────────────────────────────────────────────────

    def _build_llm(self, agent_def: dict):
        model = agent_def.get("llm_model", settings.default_llm_model)
        if model in MODEL_ALIASES:
            model = MODEL_ALIASES[model]
        if model:
            model = model.replace("openrouter/", "")

        import os
        api_key = getattr(settings, "openrouter_api_key", None) or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENROUTER_API_KEY in Railway variables.")

        return LLM(model=f"openrouter/{model}", api_key=api_key)
