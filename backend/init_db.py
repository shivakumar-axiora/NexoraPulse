"""
init_db.py
──────────
Creates all database tables from the SQLAlchemy ORM models.
Safe to run multiple times — uses CREATE TABLE IF NOT EXISTS semantics.

Usage:
  python init_db.py
"""

import sys
import os

# Make sure imports resolve from the backend root
sys.path.insert(0, os.path.dirname(__file__))

import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from db.database import engine, Base, DATABASE_URL, get_db_name_and_root_url

# Import ALL models so SQLAlchemy registers them before create_all()
from db.models import (
    Tenant,
    UserProfile,
    Survey,
    SurveyQuestion,
    SurveyResponse,
    SurveyAnswer,
    SurveyFeedback,
)

def create_db_if_not_exists():
    db_name, root_url = get_db_name_and_root_url(DATABASE_URL)
    
    # 1. First, try to connect directly to the target database.
    # If this works, the database already exists and we're good.
    try:
        target_engine = create_engine(DATABASE_URL)
        with target_engine.connect() as conn:
            print(f"Successfully connected to database '{db_name}'.")
        target_engine.dispose()
        return
    except Exception:
        print(f"Could not connect to '{db_name}' directly. Checking if it needs to be created...")

    # 2. If direct connection failed, try connecting to 'postgres' to create it
    # Create engine for 'postgres' default database
    root_engine = create_engine(root_url, isolation_level="AUTOCOMMIT")
    
    with root_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        exists = result.scalar()
        
        if not exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists but was unreachable earlier.")
    
    root_engine.dispose()

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

def run_migrations():
    """Runs alembic migrations to bring the database to the latest version."""
    print("Running database migrations (Alembic)...")
    try:
        alembic_cfg = Config("alembic.ini")
        
        # Check if we are in development mode to auto-generate migrations
        if os.getenv("ENVIRONMENT") == "development":
            # Check for changes between models and database
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                script = ScriptDirectory.from_config(alembic_cfg)
                
                # Use autogenerate to see if there are any changes
                from alembic.autogenerate import compare_metadata
                diff = compare_metadata(context, Base.metadata)
                
                if diff:
                    print("Model changes detected. Auto-generating migration...")
                    timestamp = int(time.time())
                    message = f"auto_migration_{timestamp}"
                    command.revision(alembic_cfg, message=message, autogenerate=True)
                    print(f"New migration '{message}' created.")
                else:
                    print("No model changes detected.")
            engine.dispose()

        command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"ERROR: Could not apply migrations: {e}")
        # We don't exit here because sometimes tables already exist 
        # and alembic might complain if not synced, 
        # but for a fresh setup it should work.

def init(retries=10, delay=3):
    # 1. Ensure the physical database exists
    print(f"Checking if database exists (Target: {DATABASE_URL})...")
    
    db_created_or_exists = False
    last_error = None

    for i in range(retries):
        try:
            create_db_if_not_exists()
            db_created_or_exists = True
            break
        except Exception as e:
            last_error = e
            print(f"  [Attempt {i+1}/{retries}] Could not connect to PostgreSQL: {e}")
            if i < retries - 1:
                print(f"  Waiting {delay}s before retrying...")
                time.sleep(delay)

    if not db_created_or_exists:
        print(f"\nERROR: Failed to connect to PostgreSQL after {retries} attempts.")
        print(f"Last error: {last_error}")
        print("\nPlease ensure:")
        print("  1. Your PostgreSQL server is running (e.g., 'docker-compose up -d')")
        print("  2. The credentials in .env or DATABASE_URL are correct.")
        print("  3. The server is reachable at the specified host/port.")
        sys.exit(1)

    # 2. Run migrations
    run_migrations()

    print()
    print("OK  Tables created (or already exist):")
    for table in Base.metadata.sorted_tables:
        print(f"   - {table.name}")
    print()
    print("Done. Use 'alembic revision --autogenerate -m \"description\"' to create new migrations.")

if __name__ == "__main__":
    init()
