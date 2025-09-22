from src.domain.entities.campaign_partner import CampaignPartner


class AssociatePartnerToCampaignCommand:
    def __init__(self, campaign_partner: CampaignPartner):
        self.campaign_partner = campaign_partner
