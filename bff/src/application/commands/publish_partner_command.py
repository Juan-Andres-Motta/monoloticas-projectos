from src.domain.entities.partner import Partner


class PublishPartnerCommand:
    def __init__(self, partner: Partner):
        self.partner = partner
