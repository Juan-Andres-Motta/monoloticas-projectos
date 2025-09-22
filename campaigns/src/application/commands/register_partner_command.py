from src.domain.entities.partner import Partner


class RegisterPartnerCommand:
    def __init__(self, partner: Partner):
        self.partner = partner
