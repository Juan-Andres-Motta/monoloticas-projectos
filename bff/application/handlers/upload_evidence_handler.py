from ..commands.upload_evidence_command import UploadEvidenceCommand


class UploadEvidenceHandler:
    """Handler for uploading campaign evidence - publishes to Pulsar"""

    def __init__(self, pulsar_publisher=None):
        self._pulsar_publisher = pulsar_publisher

    async def handle(self, command: UploadEvidenceCommand, user_id: str) -> dict:
        """Handle evidence upload command by publishing to Pulsar"""

        if not self._pulsar_publisher:
            raise Exception("Pulsar publisher not available")

        try:
            # Convert command objects to dicts for JSON serialization
            evidence_details_dict = {
                "platform": command.evidence_details.platform,
                "post_url": command.evidence_details.post_url,
                "post_date": command.evidence_details.post_date.isoformat(),
                "content_type": command.evidence_details.content_type,
                "engagement_metrics": {
                    "views": command.evidence_details.engagement_metrics.views,
                    "likes": command.evidence_details.engagement_metrics.likes,
                    "comments": command.evidence_details.engagement_metrics.comments,
                    "shares": command.evidence_details.engagement_metrics.shares
                }
            }

            audience_data_dict = {
                "followers_count": command.audience_data.followers_count,
                "audience_reached": command.audience_data.audience_reached,
                "demographics": {
                    "primary_country": command.audience_data.demographics.primary_country,
                    "age_range": command.audience_data.demographics.age_range
                }
            }

            # Publish command to Pulsar
            command_id = await self._pulsar_publisher.publish_evidence_upload_command(
                user_id=user_id,
                partner_id=command.partner_id,
                campaign_id=command.campaign_id,
                evidence_type=command.evidence_type,
                evidence_details=evidence_details_dict,
                audience_data=audience_data_dict,
                description=command.description
            )

            # Return immediate response with command tracking info
            response = {
                "command_id": command_id,
                "status": "PROCESSING",
                "message": "Evidence upload request submitted successfully",
                "campaign_id": command.campaign_id,
                "partner_id": command.partner_id,
                "user_id": user_id,
                "evidence_type": command.evidence_type
            }

            return response

        except Exception as e:
            print(f"❌ Error publishing evidence upload command: {e}")
            raise