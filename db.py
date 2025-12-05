# db.py
import os
from databases import Database
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(150), unique=True, nullable=False),
    Column("username", String(100), nullable=False),
    Column("phonenumber", String(20)),
    Column("salt", String(255), nullable=False),       
    Column("verifier", String(255), nullable=False)
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)