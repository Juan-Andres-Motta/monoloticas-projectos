from sqlalchemy import Table, Column, Integer, String, DateTime, Text, MetaData

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

saga_logs_table = Table(
    "saga_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("saga_id", String(255), nullable=False),
    Column("step", String(50), nullable=False),
    Column("status", String(20), nullable=False),
    Column("timestamp", DateTime, nullable=False),
    Column("details", Text, nullable=True),
)

processed_messages_table = Table(
    "processed_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("message_id", String(255), nullable=False, unique=True),
    Column("processed_at", DateTime, nullable=False),
)
