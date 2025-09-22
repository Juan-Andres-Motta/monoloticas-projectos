from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData

metadata = MetaData()

tracking_events_table = Table(
    "tracking_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("campaign_id", String(255), nullable=False),
    Column("event_type", String(50), nullable=False),
    Column("status", String(20), nullable=False, default="success"),
    Column("timestamp", DateTime, nullable=False),
)
