from uuid import uuid4
from datetime import datetime, date
from ..commands.accept_campaign_command import AcceptCampaignCommand


class AcceptCampaignHandler:
    """Handler for accepting campaign enrollment - publishes to Pulsar"""

    def __init__(self, pulsar_publisher=None):
        self._pulsar_publisher = pulsar_publisher

    async def handle(self, command: AcceptCampaignCommand, user_id: str) -> dict:
        """Handle campaign acceptance command by publishing to Pulsar"""

        if not self._pulsar_publisher:
            raise Exception("Pulsar publisher not available")

        try:
            # Convert command acceptance terms to dict
            acceptance_terms_dict = {
                "commission_type": command.acceptance_terms.commission_type,
                "commission_rate": float(command.acceptance_terms.commission_rate),
                "cookie_duration_days": command.acceptance_terms.cookie_duration_days,
                "promotional_methods": command.acceptance_terms.promotional_methods
            }

            # Publish command to Pulsar
            command_id = await self._pulsar_publisher.publish_campaign_accept_command(
                user_id=user_id,
                campaign_id=command.campaign_id,
                partner_id=command.partner_id,
                partner_type=command.partner_type,
                acceptance_terms=acceptance_terms_dict,
                estimated_monthly_reach=command.estimated_monthly_reach
            )

            # Return immediate response with command tracking info
            response = {
                "command_id": command_id,
                "status": "PROCESSING",
                "message": "Campaign acceptance request submitted successfully",
                "campaign_id": command.campaign_id,
                "partner_id": command.partner_id,
                "user_id": user_id
            }

            # TODO: In production, this would:
            # 1. Wait for response from Pulsar response topic
            # 2. Or return async tracking ID for status polling
            # 3. Handle timeout scenarios
            # 4. Provide real-time status updates via WebSocket

            return response

        except Exception as e:
            print(f"❌ Error publishing campaign accept command: {e}")
            raise