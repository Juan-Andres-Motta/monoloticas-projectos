from src.domain.entities.commission import Commission


class RegisterCommissionCommand:
    def __init__(self, commission: Commission):
        self.commission = commission
