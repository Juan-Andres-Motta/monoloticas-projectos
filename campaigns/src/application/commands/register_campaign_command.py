from src.domain.entities.campaign import Campaign


class RegisterCampaignCommand:
    def __init__(self, campaign: Campaign):
        self.campaign = campaign
