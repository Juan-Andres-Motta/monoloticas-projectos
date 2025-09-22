from pulsar.schema import Record, String


class CampaignRecord(Record):
    campaign_id = String()
    name = String()


class CampaignPartnerAssociationRecord(Record):
    campaign_id = String()
    partner_id = String()


class ContentRecord(Record):
    content_id = String()
    campaign_id = String()
    content_url = String()
