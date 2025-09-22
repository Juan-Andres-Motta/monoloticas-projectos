from pulsar.schema import Record, String


class CampaignRecord(Record):
    campaign_id = String()
    name = String()


class CampaignPartnerAssociationRecord(Record):
    campaign_id = String()
    partner_id = String()


class ContentAssociationRecord(Record):
    content_id = String()
    campaign_id = String()
    content_url = String()


class FailTrackingEventRecord(Record):
    tracking_id = String()
