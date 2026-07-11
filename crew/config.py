"""
Xcerebro 2.0 — Configuration

Loads environment variables via Pydantic settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    # ---- LLM Provider ----
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None  # used for LLM + embeddings
    deepseek_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    default_llm_model: str = "anthropic/claude-sonnet-4-5-20250929"
    default_llm_provider: str = "anthropic"

    # ---- Multi-Model Routing (v2.1+) ----
    # Tier: economy (cheapest), balanced (smart routing), premium (Claude only)
    routing_default_tier: str = "balanced"
    routing_enabled: bool = False  # Off by default in v2.0; flip to True for v2.1
    routing_max_retries: int = 2

    # ---- Database ----
    database_url: str = "postgresql://xcerebro:changeme@postgres:5432/crew"
    redis_url: str = "redis://redis:6379"

    # ---- This service ----
    port: int = 8000
    agent_runtime_url: str = "http://localhost:8000"
    agent_runtime_api_key: Optional[str] = None

    # ---- n8n integration ----
    n8n_base_url: Optional[str] = None
    n8n_api_key: Optional[str] = None
    n8n_webhook_url: Optional[str] = None
    n8n_bridge_secret: Optional[str] = None  # shared secret for agent email/calendar webhooks

    # ---- ClickUp ----
    clickup_api_key: Optional[str] = None
    clickup_team_id: Optional[str] = None

    # ---- Dify integration ----
    dify_base_url: Optional[str] = None
    dify_api_key: Optional[str] = None

    # ---- Postiz integration ----
    postiz_base_url: Optional[str] = None
    postiz_api_key: Optional[str] = None

    # ---- Slack approval ----
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None  # verifies /slack/interactions payloads
    slack_approval_channel_id: Optional[str] = None
    slack_notifications_channel_id: Optional[str] = None
    slack_chat_channel_id: Optional[str] = None  # dedicated #xcerebro chat channel; bot answers everything there

    # ---- Graduated autonomy ----
    # Clean approvals per (agent, action_type) before the weekly digest
    # proposes flipping auto_approve. A human flips it, never the system.
    trust_auto_approve_threshold: int = 10

    # ---- Cost controls ----
    max_tokens_per_task: int = 4000
    max_tasks_per_hour: int = 120
    max_daily_llm_spend_usd: float = 50.0

    # ---- Approval defaults ----
    approval_required_for_dm: bool = True
    approval_required_for_email: bool = True
    approval_required_for_public_post: bool = True
    approval_required_for_crm_update: bool = False
    approval_required_for_calendar_booking: bool = False
    approval_required_for_refund: bool = True
    approval_required_for_payment: bool = True
    approval_required_for_task_management: bool = True  # ClickUp create/delete/assignee changes

    # ---- Logging ----
    log_level: str = "info"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
