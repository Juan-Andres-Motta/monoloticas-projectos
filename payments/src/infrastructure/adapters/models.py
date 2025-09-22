from sqlalchemy import Table, Column, Integer, String, Float, Text, MetaData

metadata = MetaData()

payments_table = Table(
    "payments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("amount", Float, nullable=False),
    Column("currency", String(10), nullable=False),
    Column("payment_method", String(50), nullable=False),
    Column("account_details", Text, nullable=False),  # JSON as text
    Column("user_id", String(255), nullable=False),
)
