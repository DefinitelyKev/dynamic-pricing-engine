import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from app.models.base import Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = f"{settings.DATABASE_URL}_test"


def create_test_database():
    """Create test database if it doesn't exist."""
    if not database_exists(TEST_DATABASE_URL):
        create_database(TEST_DATABASE_URL)


def drop_test_database():
    """Drop test database if it exists."""
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def test_db():
    """Create test database and tables."""
    create_test_database()
    engine = create_engine(TEST_DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables and database after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    drop_test_database()


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a fresh database session for a test."""
    connection = test_db.connect()
    transaction = connection.begin()

    # Create session bound to the connection
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    # Rollback the transaction and close the session
    session.close()
    transaction.rollback()
    connection.close()


def test_database_connection(db_session):
    """Test that we can connect to the database."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_table_creation(db_session):
    """Test that all tables were created."""
    # Get list of all tables
    result = db_session.execute(
        text(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
        )
    )
    tables = [row[0] for row in result]

    # Check for our core tables
    assert "property" in tables
    assert "pricingrule" in tables
    assert "pricehistory" in tables
    assert "marketdata" in tables
