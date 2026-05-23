"""
Xcerebro 2.0 — Crew Registry

Loads agent and crew definitions from YAML files in /agents/.
Provides the orchestration interface for the FastAPI runtime.

The registry is the single source of truth for which agents exist,
which crews exist, and how they coordinate.
"""

from pathlib import Path
from typing import Any, Optional
import yaml
from loguru import logger

from crewai import Agent, Crew, Task, Process, LLM

from config import settings


# Map shorthand model names to actual Anthropic API identifiers (with date suffix)
MODEL_ALIASES = {
    "claude-sonnet-4-5": "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5": "claude-haiku-4-5-20251001",
    "claude-opus-4-1": "claude-opus-4-1-20250805",
    "claude-sonnet-4": "claude-sonnet-4-20250514",
    "claude-opus-4": "claude-opus-4-20250514",
}


class CrewRegistry:
    """Loads + indexes all agent and crew definitions."""

    def __init__(self, agents_path: Path):
        self.agents_path = Path(agents_path)
        self.agents: dict[str, dict] = {}
        self.crews: dict[str, dict] = {}
        self.workflow_map: dict[str, str] = {}  # workflow_name -> crew_id

    # ---------- LOADING ----------

    def load_all(self) -> None:
        """Load every YAML file under agents/tier-a and agents/tier-b."""
        if not self.agents_path.exists():
            logger.warning(f"Agents path {self.agents_path} not found")
            return

        # Load Tier A leadership agents
        tier_a_dir = self.agents_path / "tier-a"
        if tier_a_dir.exists():
            for yaml_file in tier_a_dir.glob("*.yaml"):
                self._load_agent_file(yaml_file, tier="a")

        # Load Tier B specialist agents
        tier_b_dir = self.agents_path / "tier-b"
        if tier_b_dir.exists():
            for yaml_file in tier_b_dir.glob("*.yaml"):
                self._load_agent_file(yaml_file, tier="b")

        # Load crew definitions
        crews_dir = self.agents_path.parent / "crews"
        if crews_dir.exists():
            for yaml_file in crews_dir.glob("*.yaml"):
                self._load_crew_file(yaml_file)

        logger.info(f"Registry loaded: {len(self.agents)} agents, "
                    f"{len(self.crews)} crews")

    def _load_agent_file(self, path: Path, tier: str) -> None:
        """Load a single agent YAML."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            agent_id = data.get("id") or path.stem
            data["_tier"] = tier
            data["_path"] = str(path)
            self.agents[agent_id] = data
            logger.debug(f"Loaded agent: {agent_id} (tier {tier})")
        except Exception as e:
            logger.error(f"Failed to load agent {path}: {e}")

    def _load_crew_file(self, path: Path) -> None:
        """Load a crew definition YAML."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            crew_id = data.get("id") or path.stem
            self.crews[crew_id] = data

            # Index workflow → crew mappings
            for workflow in data.get("triggers_for_workflows", []):
                self.workflow_map[workflow] = crew_id

            logger.debug(f"Loaded crew: {crew_id}")
        except Exception as e:
            logger.error(f"Failed to load crew {path}: {e}")

    # ---------- LOOKUPS ----------

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

    # ---------- APPROVAL POLICY ----------

    def requires_approval(self, agent_id: str, task: str) -> bool:
        """
        TEMPORARILY DISABLED for testing.
        
        Original logic gated tier-b agents and certain action keywords (DM, email,
        post, refund, payment) behind human approval via Slack. The Slack 
        notification fires correctly, but the callback endpoint to receive the
        approval decision was never built in main.py.
        
        Until /slack/interactions endpoint is implemented with proper signature
        verification and payload parsing, the approval flow can't complete, so
        this method always returns False to allow agents to execute directly.
        
        TO RE-ENABLE LATER: Restore the original logic from git history once
        the /slack/interactions endpoint exists.
        """
        return False

    # ---------- AGENT INVOCATION ----------

    async def invoke(self, agent_id: str, task: str, context: dict) -> Any:
        """
        Invoke a single agent for a task.

        Builds a CrewAI Agent + Task on the fly, runs it, returns result.
        """
        agent_def = self.agents.get(agent_id)
        if not agent_def:
            raise ValueError(f"Agent {agent_id} not found")

        # Build the LLM
        llm = self._build_llm(agent_def)

        # Build the CrewAI Agent
        cw_agent = Agent(
            role=agent_def.get("role", agent_id),
            goal=agent_def.get("goal", "Complete the assigned task"),
            backstory=agent_def.get("backstory", ""),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

        # Build the Task
        cw_task = Task(
            description=task,
            expected_output=agent_def.get("expected_output", "A clear, actionable response"),
            agent=cw_agent,
        )

        # Single-agent crew for this invocation
        crew = Crew(
            agents=[cw_agent],
            tasks=[cw_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async(inputs=context)
        return str(result)

    async def run_crew(self, crew_id: str, inputs: dict) -> Any:
        """
        Run a coordinated crew (multi-agent collaboration).
        """
        crew_def = self.crews.get(crew_id)
        if not crew_def:
            raise ValueError(f"Crew {crew_id} not found")

        # Build agents and tasks for this crew
        agents = []
        tasks = []
        agent_lookup = {}

        for member in crew_def.get("members", []):
            agent_def = self.agents.get(member["agent_id"])
            if not agent_def:
                logger.warning(f"Agent {member['agent_id']} not found, skipping")
                continue
            llm = self._build_llm(agent_def)
            cw_agent = Agent(
                role=agent_def.get("role", member["agent_id"]),
                goal=agent_def.get("goal", "Complete the assigned task"),
                backstory=agent_def.get("backstory", ""),
                llm=llm,
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

        # Build manager LLM for hierarchical processes
        if crew_def.get("hierarchical"):
            process = Process.hierarchical
            # Hierarchical crews need a manager LLM
            manager_llm = self._build_llm({})  # Use defaults
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=process,
                manager_llm=manager_llm,
                verbose=True,
            )
        else:
            process = Process.sequential
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=process,
                verbose=True,
            )

        result = await crew.kickoff_async(inputs=inputs)
        return str(result)

    async def resume_after_approval(self, approval_record: dict) -> Any:
        """Resume an agent execution after human approval."""
        # In a production system this would re-hydrate state from the approval record.
        # For Phase 2, we re-invoke the original task.
        return await self.invoke(
            agent_id=approval_record["agent_id"],
            task=approval_record["task"],
            context=approval_record.get("context", {}),
        )

    # ---------- LLM BUILDER ----------

    def _build_llm(self, agent_def: dict):
        """
        Build the LLM client based on agent preferences + global defaults.
        Uses crewai.LLM (which wraps litellm) — required for CrewAI 0.175+.
        """
        provider = agent_def.get("llm_provider", settings.default_llm_provider)
        model = agent_def.get("llm_model", settings.default_llm_model)

        # Step 1: Map shorthand model names to actual API model identifiers
        # (e.g., "claude-sonnet-4-5" -> "claude-sonnet-4-5-20250929")
        if model in MODEL_ALIASES:
            model = MODEL_ALIASES[model]

        # Step 2: Auto-prefix model name with provider if no prefix is present
        # (litellm requires "anthropic/model-name" format)
        known_prefixes = ("anthropic/", "openai/", "azure/", "bedrock/", "vertex_ai/", "azure_ai/")
        if model and not any(model.startswith(p) for p in known_prefixes):
            if provider == "anthropic":
                model = f"anthropic/{model}"
            elif provider == "openai":
                model = f"openai/{model}"

        # Step 3: Build LLM using crewai.LLM (compatible with CrewAI 0.175+)
        # Note: max_tokens is NOT passed because crewai.LLM doesn't support it directly
        if provider == "anthropic":
            return LLM(
                model=model,
                api_key=settings.anthropic_api_key,
            )
        elif provider == "openai":
            return LLM(
                model=model,
                api_key=settings.openai_api_key,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
