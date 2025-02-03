import os
import sys
from sqlalchemy_utils import database_exists, drop_database, create_database

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.base import Base
from app.core.database import engine


def reset_database():
    """Drop and recreate the database"""
    database_url = settings.DATABASE_URL

    print(f"Using database URL: {database_url}")

    # Drop database if it exists
    if database_exists(database_url):
        print("Dropping existing database...")
        drop_database(database_url)

    # Create new database
    print("Creating new database...")
    create_database(database_url)

    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    print("Database reset complete!")


if __name__ == "__main__":
    reset_database()
