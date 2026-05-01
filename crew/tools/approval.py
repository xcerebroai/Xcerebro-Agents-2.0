"""
Xcerebro 2.0 — Approval Manager

Sends approval requests to Slack and tracks pending approvals.
Resolves them when the human clicks approve/reject.

In production, the Slack message uses Block Kit interactive buttons that
post back to /approvals/{approval_id}. For Phase 2 MVP, we use simple
formatted messages and require the buyer to manually call the endpoint.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Optional

from loguru import logger
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError


class ApprovalManager:
    """Tracks pending approvals + posts to Slack."""

    def __init__(self, slack_token: Optional[str], approval_channel: Optional[str]):
        self.slack_token = slack_token
        self.approval_channel = approval_channel
        self.pending: dict[str, dict] = {}
        self.slack_client: Optional[AsyncWebClient] = None

        if slack_token:
            try:
                self.slack_client = AsyncWebClient(token=slack_token)
                logger.info("Slack approval manager initialized")
            except Exception as e:
                logger.error(f"Failed to init Slack client: {e}")

    async def request(
        self,
        title: str,
        description: str,
        context: dict,
        invocation_id: str,
    ) -> str:
        """
        Create a new approval request.

        Returns the approval_id. The caller is paused until /approvals/{id}
        is called with a decision.
        """
        approval_id = str(uuid.uuid4())
        record = {
            "id": approval_id,
            "title": title,
            "description": description,
            "context": context,
            "invocation_id": invocation_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        self.pending[approval_id] = record

        # Post to Slack
        if self.slack_client and self.approval_channel:
            try:
                await self.slack_client.chat_postMessage(
                    channel=self.approval_channel,
                    text=f"🔔 Approval needed: {title}",
                    blocks=self._build_approval_blocks(record),
                )
                logger.info(f"Approval {approval_id} posted to Slack")
            except SlackApiError as e:
                logger.error(f"Slack post failed: {e}")
        else:
            logger.warning(f"Approval {approval_id} created but no Slack configured")

        return approval_id

    async def resolve(
        self,
        approval_id: str,
        decision: str,
        approver: str,
        note: Optional[str] = None,
    ) -> dict:
        """Mark an approval as resolved (approve or reject)."""
        record = self.pending.get(approval_id)
        if not record:
            raise ValueError(f"Approval {approval_id} not found or already resolved")

        record["status"] = decision
        record["approver"] = approver
        record["note"] = note
        record["resolved_at"] = datetime.utcnow().isoformat()

        # Post resolution to Slack
        if self.slack_client and self.approval_channel:
            emoji = "✅" if decision == "approve" else "❌"
            try:
                await self.slack_client.chat_postMessage(
                    channel=self.approval_channel,
                    text=f"{emoji} {record['title']} → {decision} by {approver}",
                )
            except SlackApiError as e:
                logger.error(f"Slack resolution post failed: {e}")

        # Don't delete — keep for audit
        record_copy = dict(record)
        return record_copy

    def get_pending(self) -> list[dict]:
        """List all pending approvals."""
        return [r for r in self.pending.values() if r.get("status") == "pending"]

    @staticmethod
    def _build_approval_blocks(record: dict) -> list[dict]:
        """Build Slack Block Kit message for an approval request."""
        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔔 {record['title']}"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{record['description']}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Approval ID:* `{record['id']}`",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "value": f"approve:{record['id']}",
                        "action_id": "approval_approve",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "value": f"reject:{record['id']}",
                        "action_id": "approval_reject",
                    },
                ],
            },
        ]
