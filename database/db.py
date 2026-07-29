from sqlalchemy import create_engine
from database.models import metadata

DATABASE_URL = "postgresql://postgres:sowji%402005@db:5432/honeypot"

engine = create_engine(DATABASE_URL)

metadata.create_all(engine)

print("Database Connected Successfully")
print("Table Created Successfully")