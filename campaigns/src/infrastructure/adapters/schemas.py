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
