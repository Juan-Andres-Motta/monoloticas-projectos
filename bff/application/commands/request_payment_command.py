from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
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


@dataclass
class AccountInfo:
    account_type: AccountType
    last_four_digits: str
    account_holder: str


@dataclass
class PaymentDetails:
    requested_amount: Decimal
    currency: str
    payment_method: PaymentMethod
    account_info: AccountInfo


@dataclass
class CommissionPeriod:
    start_date: date
    end_date: date
    included_campaigns: List[str]


@dataclass
class InvoiceDetails:
    invoice_required: bool
    tax_id: str
    business_name: str


@dataclass
class RequestPaymentCommand:
    partner_id: str
    request_type: RequestType
    payment_details: PaymentDetails
    commission_period: CommissionPeriod
    invoice_details: InvoiceDetails