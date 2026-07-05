"""
Xcerebro 2.0 — ClickUp Tools

Task management access via the ClickUp API v2.
Requires CLICKUP_API_KEY (personal token) and CLICKUP_TEAM_ID in env.
"""

import json
import os
from typing import Type

import requests
from crewai.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

CLICKUP_BASE = "https://api.clickup.com/api/v2"


def _headers() -> dict:
    return {
        "Authorization": os.getenv("CLICKUP_API_KEY", ""),
        "Content-Type": "application/json",
    }


def _safe_request(method: str, url: str, **kwargs) -> dict:
    if not os.getenv("CLICKUP_API_KEY"):
        return {"error": "CLICKUP_API_KEY not configured in environment."}
    try:
        resp = requests.request(method, url, headers=_headers(), timeout=15, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        logger.error(f"ClickUp API error {e.response.status_code}: {e.response.text[:300]}")
        return {"error": str(e), "status_code": e.response.status_code}
    except Exception as e:
        logger.error(f"ClickUp request failed: {e}")
        return {"error": str(e)}


class ReadTasksInput(BaseModel):
    list_id: str = Field(default="", description="ClickUp list ID to read tasks from. Empty = list the team's spaces/lists so you can find one.")
    include_closed: bool = Field(default=False, description="Include completed tasks")


class ClickUpReadTasksTool(BaseTool):
    name: str = "clickup_read_tasks"
    description: str = (
        "Read tasks from ClickUp. With no list_id, returns the team's spaces and "
        "lists (use this first to discover IDs). With a list_id, returns its tasks: "
        "name, status, assignees, due date, priority."
    )
    args_schema: Type[BaseModel] = ReadTasksInput

    def _run(self, list_id: str = "", include_closed: bool = False) -> str:
        team_id = os.getenv("CLICKUP_TEAM_ID", "")
        if not list_id:
            if not team_id:
                return json.dumps({"error": "CLICKUP_TEAM_ID not configured."})
            spaces = _safe_request("GET", f"{CLICKUP_BASE}/team/{team_id}/space")
            if "error" in spaces:
                return json.dumps(spaces)
            out = []
            for space in spaces.get("spaces", []):
                lists = _safe_request("GET", f"{CLICKUP_BASE}/space/{space['id']}/list")
                out.append({
                    "space": space["name"],
                    "space_id": space["id"],
                    "lists": [{"id": l["id"], "name": l["name"]} for l in lists.get("lists", [])],
                })
            return json.dumps({"spaces": out})

        params = {"include_closed": str(include_closed).lower()}
        data = _safe_request("GET", f"{CLICKUP_BASE}/list/{list_id}/task", params=params)
        if "error" in data:
            return json.dumps(data)
        tasks = [
            {
                "id": t["id"],
                "name": t["name"],
                "status": (t.get("status") or {}).get("status"),
                "assignees": [a.get("username") for a in t.get("assignees", [])],
                "due_date": t.get("due_date"),
                "priority": (t.get("priority") or {}).get("priority"),
                "url": t.get("url"),
            }
            for t in data.get("tasks", [])
        ]
        return json.dumps({"task_count": len(tasks), "tasks": tasks})


class CreateTaskInput(BaseModel):
    list_id: str = Field(description="ClickUp list ID to create the task in")
    name: str = Field(description="Task title")
    description: str = Field(default="", description="Task description/details")
    due_date_ms: int = Field(default=0, description="Optional due date as unix epoch milliseconds")


class ClickUpCreateTaskTool(BaseTool):
    name: str = "clickup_create_task"
    description: str = "Create a task in a ClickUp list. Use clickup_read_tasks with no list_id first to find list IDs."
    args_schema: Type[BaseModel] = CreateTaskInput

    def _run(self, list_id: str, name: str, description: str = "", due_date_ms: int = 0) -> str:
        payload: dict = {"name": name, "description": description}
        if due_date_ms:
            payload["due_date"] = due_date_ms
        data = _safe_request("POST", f"{CLICKUP_BASE}/list/{list_id}/task", json=payload)
        if "error" in data:
            return json.dumps(data)
        return json.dumps({"ok": True, "task_id": data.get("id"), "url": data.get("url")})


CLICKUP_TOOL_REGISTRY: dict[str, type] = {
    "clickup.read_tasks": ClickUpReadTasksTool,
    "clickup.create_task": ClickUpCreateTaskTool,
}


def get_clickup_tools(tool_names: list[str]) -> list:
    tools = []
    for name in tool_names:
        cls = CLICKUP_TOOL_REGISTRY.get(name)
        if cls:
            tools.append(cls())
    return tools
