"""
Xcerebro 2.0 — Agent Memory Manager

Persistent semantic memory backed by Postgres + pgvector.
Embeddings run through OpenRouter's OpenAI-compatible endpoint
so no separate OpenAI API key is required.

Each agent invocation:
  1. retrieve() — pulls semantically relevant past memories
  2. (agent runs with that context injected)
  3. store()    — writes the result as a new memory

Memory is shared across agents — the CEO can read what the CFO wrote.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# ── schema ────────────────────────────────────────────────────────────────────

MIGRATION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS agent_memories (
    id          SERIAL PRIMARY KEY,
    agent_id    VARCHAR(64)  NOT NULL,
    memory_type VARCHAR(32)  NOT NULL DEFAULT 'episodic',
    content     TEXT         NOT NULL,
    embedding   vector(1536),
    metadata    JSONB        NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_memories_agent_date
    ON agent_memories (agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_memories_embedding
    ON agent_memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100)
    WHERE embedding IS NOT NULL;
"""


class MemoryManager:
    """Persistent agent memory with semantic retrieval via pgvector."""

    def __init__(self, database_url: str, openrouter_api_key: str = ""):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self._api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY", "")
        self._migrate()

    # ── setup ─────────────────────────────────────────────────────────────────

    def _migrate(self) -> None:
        """Create tables and indexes if they don't exist."""
        try:
            with self.engine.connect() as conn:
                for stmt in MIGRATION_SQL.strip().split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        conn.execute(text(stmt))
                conn.commit()
            logger.info("MemoryManager: schema ready")
        except SQLAlchemyError as e:
            # pgvector extension may not be available — degrade gracefully
            logger.warning(f"MemoryManager: migration issue (degraded mode): {e}")

    # ── embeddings ────────────────────────────────────────────────────────────

    def _embed(self, text_input: str) -> Optional[list[float]]:
        """
        Embed text via OpenRouter's OpenAI-compatible embeddings endpoint.
        Returns None if the API key is missing or the call fails.
        """
        if not self._api_key:
            return None
        try:
            import openai
            client = openai.OpenAI(
                api_key=self._api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            response = client.embeddings.create(
                model="openai/text-embedding-3-small",
                input=text_input[:8000],  # stay within token limit
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"MemoryManager: embedding failed, using text search: {e}")
            return None

    # ── write ─────────────────────────────────────────────────────────────────

    def store(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[dict] = None,
    ) -> None:
        """Persist a memory. Call after each agent invocation."""
        embedding = self._embed(content)
        meta = json.dumps(metadata or {})
        vec_literal = f"'[{','.join(str(v) for v in embedding)}]'" if embedding else "NULL"

        sql = text(f"""
            INSERT INTO agent_memories (agent_id, memory_type, content, embedding, metadata)
            VALUES (:agent_id, :memory_type, :content, {vec_literal}::vector, :metadata::jsonb)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(sql, {
                    "agent_id": agent_id,
                    "memory_type": memory_type,
                    "content": content,
                    "metadata": meta,
                })
                conn.commit()
        except SQLAlchemyError as e:
            logger.error(f"MemoryManager.store failed: {e}")

    # ── read ──────────────────────────────────────────────────────────────────

    def retrieve(
        self,
        agent_id: str,
        query: str,
        top_k: int = 5,
        any_agent: bool = False,
    ) -> list[dict]:
        """
        Return the most relevant memories for this agent.

        If embeddings are available: semantic (cosine) search.
        If not: recency fallback (last top_k memories).

        Set any_agent=True to search across ALL agents (useful for CEO
        querying what CFO or CMO agents wrote).
        """
        embedding = self._embed(query)
        agent_filter = "" if any_agent else "AND agent_id = :agent_id"

        if embedding:
            vec_literal = f"'[{','.join(str(v) for v in embedding)}]'"
            sql = text(f"""
                SELECT agent_id, memory_type, content, metadata, created_at,
                       1 - (embedding <=> {vec_literal}::vector) AS similarity
                FROM agent_memories
                WHERE embedding IS NOT NULL {agent_filter}
                ORDER BY embedding <=> {vec_literal}::vector
                LIMIT :top_k
            """)
        else:
            # Recency fallback — no vector available
            sql = text(f"""
                SELECT agent_id, memory_type, content, metadata, created_at,
                       1.0 AS similarity
                FROM agent_memories
                WHERE 1=1 {agent_filter}
                ORDER BY created_at DESC
                LIMIT :top_k
            """)

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(sql, {"agent_id": agent_id, "top_k": top_k}).fetchall()
            return [
                {
                    "agent_id": r.agent_id,
                    "memory_type": r.memory_type,
                    "content": r.content,
                    "metadata": r.metadata,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "similarity": float(r.similarity),
                }
                for r in rows
            ]
        except SQLAlchemyError as e:
            logger.error(f"MemoryManager.retrieve failed: {e}")
            return []

    def format_for_context(self, memories: list[dict]) -> str:
        """
        Format retrieved memories as a readable context block to inject
        into the agent's task description.
        """
        if not memories:
            return ""
        lines = ["--- Relevant past context ---"]
        for m in memories:
            ts = m.get("created_at", "")[:10] if m.get("created_at") else "?"
            lines.append(f"[{ts} | {m['agent_id']}] {m['content'][:400]}")
        lines.append("--- End past context ---")
        return "\n".join(lines)
