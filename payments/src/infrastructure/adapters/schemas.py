from pulsar.schema import Record, String, Float, Map


class PaymentRecord(Record):
    amount = Float()
    currency = String()
    payment_method = String()
    account_details = String()  # JSON string of account details
    user_id = String()
