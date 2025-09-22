from pydantic import BaseModel


class CampaignPartner(BaseModel):
    campaign_id: str
    partner_id: str
