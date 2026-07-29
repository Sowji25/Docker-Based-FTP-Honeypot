from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

credentials = Table(
    "credentials",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100)),
    Column("password", String(100)),
    Column("ip_address", String(50)),
    Column("login_time", String(100))
)