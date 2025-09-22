from pydantic import BaseModel


class Payment(BaseModel):
    amount: float
    currency: str
    payment_method: str
    account_details: str  # JSON string
    user_id: str
