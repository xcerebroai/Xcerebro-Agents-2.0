"""
Xcerebro 2.0 — Chat comms layer

One handler behind POST /chat and /slack/events: routes a human chat
message from any channel (slack / telegram / whatsapp / clickup) to an
agent, keeps a rolling conversation window in comms.messages, and
returns the reply text for the channel adapter to deliver.

Routing: a message starting with "@<agent-id> " goes to that agent;
everything else goes to the CEO (the EOS Integrator), who delegates.
"""

import re
import uuid
from typing import Any

from loguru import logger
from sqlalchemy import create_engine, text

from config import settings

MIGRATION_SQL = """
CREATE SCHEMA IF NOT EXISTS comms;

CREATE TABLE IF NOT EXISTS comms.messages (
    id              SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    channel         TEXT NOT NULL,
    role            TEXT NOT NULL,
    sender          TEXT,
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_comms_messages_conv
    ON comms.messages(conversation_id, id DESC)
"""

DEFAULT_AGENT = "auto-ceo"
HISTORY_WINDOW = 10  # ponytail: last-10 window, add summarization if threads get long

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        try:
            with _engine.connect() as conn:
                for stmt in MIGRATION_SQL.strip().split(";"):
                    if stmt.strip():
                        conn.execute(text(stmt))
                conn.commit()
        except Exception as e:
            logger.warning(f"comms: migration issue: {e}")
    return _engine


def _load_history(conversation_id: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text(
                "SELECT role, sender, content FROM comms.messages "
                "WHERE conversation_id = :cid ORDER BY id DESC LIMIT :n"
            ),
            {"cid": conversation_id, "n": HISTORY_WINDOW},
        ).fetchall()
    return [
        {"role": r[0], "sender": r[1], "content": r[2]}
        for r in reversed(rows)
    ]


def _store(conversation_id: str, channel: str, role: str, sender: str, content: str) -> None:
    with _get_engine().connect() as conn:
        conn.execute(
            text(
                "INSERT INTO comms.messages (conversation_id, channel, role, sender, content) "
                "VALUES (:cid, :ch, :role, :sender, :content)"
            ),
            {"cid": conversation_id, "ch": channel, "role": role,
             "sender": sender, "content": content[:8000]},
        )
        conn.commit()


def resolve_agent(message: str, registry) -> tuple[str, str]:
    """'@auto-cfo what's my cash?' → ('auto-cfo', "what's my cash?"). Default: CEO."""
    m = re.match(r"@([a-z0-9][a-z0-9-]*)\s+(.+)", message.strip(), re.S)
    if m and registry.get_agent(m.group(1)):
        return m.group(1), m.group(2).strip()
    return DEFAULT_AGENT, message.strip()


def _format_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = [f"{h['sender'] or h['role']}: {h['content'][:600]}" for h in history]
    return "Recent conversation:\n" + "\n".join(lines) + "\n\n"


async def handle_chat(app, channel: str, conversation_id: str, sender: str, message: str) -> dict:
    """Route one inbound chat message to an agent; return {'agent_id', 'reply'}."""
    registry = app.state.registry
    audit = app.state.audit

    agent_id, clean_message = resolve_agent(message, registry)
    if not clean_message:
        return {"agent_id": agent_id, "reply": "I got an empty message — what do you need?"}

    history = _load_history(conversation_id)
    _store(conversation_id, channel, "user", sender, clean_message)

    invocation_id = str(uuid.uuid4())
    audit.log_event(
        event_type="chat.message",
        agent_id=agent_id,
        invocation_id=invocation_id,
        payload={"channel": channel, "conversation_id": conversation_id,
                 "sender": sender, "text": clean_message[:500]},
    )

    task = (
        f"You received a chat message from {sender or 'the owner'} via {channel}.\n\n"
        f"{_format_history(history)}"
        f"New message: {clean_message}\n\n"
        "Reply as a direct chat message: conversational, concise, no report headers. "
        "Use your tools to answer with real data instead of guessing. "
        "If the request belongs to another team member's domain, answer with what "
        "you know and say who owns it."
    )

    # Same governance gate as /agents/{id}/invoke — chat is not a side door
    gate_needed, action_type = registry.requires_approval(agent_id, clean_message)
    if gate_needed:
        approval_id = await app.state.approval.request(
            title=f"Approve {agent_id} action (via {channel} chat)",
            description=clean_message,
            context={"channel": channel, "conversation_id": conversation_id, "sender": sender},
            invocation_id=invocation_id,
            agent_id=agent_id,
            action_type=action_type,
        )
        reply = (
            f"That needs a human sign-off ({action_type}). "
            f"I sent an approval card to Slack — approve it there and I'll run it."
        )
        _store(conversation_id, channel, "assistant", agent_id, reply)
        return {"agent_id": agent_id, "reply": reply, "approval_id": approval_id}

    try:
        result: Any = await registry.invoke(
            agent_id=agent_id,
            task=task,
            context={"channel": channel, "conversation_id": conversation_id},
        )
        reply = str(result).strip() or "(no reply)"
    except Exception as e:
        logger.exception(f"chat: {agent_id} failed")
        audit.log_event(
            event_type="chat.error",
            agent_id=agent_id,
            invocation_id=invocation_id,
            payload={"error": str(e)},
        )
        reply = f"Something broke on my end running that ({str(e)[:200]}). Try again or rephrase."

    _store(conversation_id, channel, "assistant", agent_id, reply)
    audit.log_event(
        event_type="chat.reply",
        agent_id=agent_id,
        invocation_id=invocation_id,
        payload={"channel": channel, "reply_preview": reply[:500]},
    )
    return {"agent_id": agent_id, "reply": reply}
