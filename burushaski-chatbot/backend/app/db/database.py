from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env properly
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# Read DATABASE_URL from environment; fall back to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local.db"
    print("WARNING: DATABASE_URL not set — falling back to local SQLite './local.db'")

# Attempt to create engine; if PostgreSQL driver missing, fall back to SQLite
try:
    engine = create_engine(DATABASE_URL)
except ModuleNotFoundError as e:
    # If psycopg2 is missing for PostgreSQL, fall back to SQLite
    if "psycopg2" in str(e):
        print(f"WARNING: psycopg2 not installed — falling back to local SQLite './local.db'")
        DATABASE_URL = "sqlite:///./local.db"
        engine = create_engine(DATABASE_URL)
    else:
        raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        