from pulsar.schema import Record, String, Float


class TrackingEventRecord(Record):
    campaign_id = String()
    event_type = String()
    timestamp = String()  # ISO string


class CommissionRecord(Record):
    amount = Float()
    campaign_id = String()
    commission_type = String()
    tracking_id = String()


class FailTrackingEventRecord(Record):
    tracking_id = String()
