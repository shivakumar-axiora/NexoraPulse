"""
db/database.py
──────────────
SQLAlchemy engine, session factory and Base.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nexpulseuser:nexpulsepass@127.0.0.1:5432/nexpulsedb")

def get_db_name_and_root_url(url: str):
    """Parses the DB URL to return the database name and a URL to connect to 'postgres' system db."""
    parsed = urlparse(url)
    db_name = parsed.path.lstrip('/')
    
    # Create a new URL pointing to 'postgres' database to perform administrative tasks
    # Replaces the path with '/postgres'
    root_parsed = parsed._replace(path='/postgres')
    return db_name, urlunparse(root_parsed)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Detect stale connections before using them
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
