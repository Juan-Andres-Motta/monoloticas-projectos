from pydantic import BaseModel
from typing import List
from datetime import date
from decimal import Decimal
from enum import Enum


class RequestType(str, Enum):
    STANDARD = "STANDARD"
    URGENT = "URGENT"
    PARTIAL = "PARTIAL"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"


class AccountType(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class AccountInfo(BaseModel):
    account_type: AccountType
    last_four_digits: str
    account_holder: str


class PaymentDetails(BaseModel):
    requested_amount: Decimal
    currency: str
    payment_method: PaymentMethod
    account_info: AccountInfo


class CommissionPeriod(BaseModel):
    start_date: date
    end_date: date
    included_campaigns: List[str]


class InvoiceDetails(BaseModel):
    invoice_required: bool
    tax_id: str
    business_name: str


class RequestPaymentRequest(BaseModel):
    partner_id: str
    request_type: RequestType
    payment_details: PaymentDetails
    commission_period: CommissionPeriod
    invoice_details: InvoiceDetails