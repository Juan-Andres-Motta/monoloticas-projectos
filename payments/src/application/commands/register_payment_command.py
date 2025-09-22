from src.domain.entities.payment import Payment


class RegisterPaymentCommand:
    def __init__(self, payment: Payment):
        self.payment = payment
