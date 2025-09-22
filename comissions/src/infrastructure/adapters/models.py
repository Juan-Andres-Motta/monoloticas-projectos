from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Text, MetaData

metadata = MetaData()

commissions_table = Table(
    "commissions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("amount", Float, nullable=False),
    Column("partner_id", String(255), nullable=False),
    Column("campaign_id", String(255), nullable=False),
    Column("commission_type", String(50), nullable=False),
    Column("tracking_id", String(255), nullable=False),
    Column("status", String(20), nullable=False, default="success"),
    Column("created_at", DateTime, nullable=False),
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

# Table for querying campaigns db
campaign_partners_table = Table(
    "campaign_partners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("campaign_id", String(255), nullable=False),
    Column("partner_id", String(255), nullable=False),
)
