from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData

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

# Table for querying campaigns db
campaign_partners_table = Table(
    "campaign_partners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("campaign_id", String(255), nullable=False),
    Column("partner_id", String(255), nullable=False),
)
