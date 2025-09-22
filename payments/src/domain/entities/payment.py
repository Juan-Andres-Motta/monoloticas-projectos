from pydantic import BaseModel
from typing import Dict, Any


class Payment(BaseModel):
    amount: float
    currency: str
    payment_method: str
    account_details: Dict[str, Any]  # JSON for account details
    user_id: str
