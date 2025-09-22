from pulsar.schema import Record, String, Integer, Float, Array


class AcceptanceTermsRecord(Record):
    commission_type = String()
    commission_rate = Float()
    cookie_duration_days = Integer()
    promotional_methods = Array(String())


class PartnerRecord(Record):
    partner_id = String()
    partner_type = String()
    acceptance_terms = AcceptanceTermsRecord()
    estimated_monthly_reach = Integer()


class TrackingEventRecord(Record):
    campaign_id = String()
    event_type = String()
    timestamp = String()  # ISO string


class PaymentRecord(Record):
    amount = Float()
    currency = String()
    payment_method = String()
    account_details = String()  # JSON string
    user_id = String()
