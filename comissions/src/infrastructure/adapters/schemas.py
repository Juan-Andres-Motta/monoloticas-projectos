from pulsar.schema import Record, String, Float


class CommissionRecord(Record):
    amount = Float()
    campaign_id = String()
    commission_type = String()
    tracking_id = String()


class FailTrackingEventRecord(Record):
    tracking_id = String()
