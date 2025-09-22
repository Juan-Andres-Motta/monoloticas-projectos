from sqlalchemy import Table, Column, Integer, String, Text, MetaData

metadata = MetaData()

partners_table = Table(
    "partners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("partner_id", String(255), nullable=False),
    Column("partner_type", String(255), nullable=False),
    Column("acceptance_terms", Text, nullable=False),  # JSON as text
    Column("estimated_monthly_reach", Integer, nullable=False),
)

campaigns_table = Table(
    "campaigns",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("campaign_id", String(255), nullable=False),
    Column("name", String(255), nullable=False),
)

campaign_partners_table = Table(
    "campaign_partners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("campaign_id", String(255), nullable=False),
    Column("partner_id", String(255), nullable=False),
)

contents_table = Table(
    "contents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("content_id", String(255), nullable=False),
    Column("campaign_id", String(255), nullable=False),
    Column("content_url", Text, nullable=False),
)
