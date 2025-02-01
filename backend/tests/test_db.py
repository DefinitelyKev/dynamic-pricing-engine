import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, close_all_sessions
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists, create_database, drop_database
from app.models.base import Base
from app.models.property import Property, PriceHistory, MarketData
from app.models.pricing import PricingRule
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = f"{settings.DATABASE_URL}_test"


def create_test_database():
    """Create test database if it doesn't exist."""
    try:
        if not database_exists(TEST_DATABASE_URL):
            create_database(TEST_DATABASE_URL)
    except Exception as e:
        print(f"Error creating database: {e}")
        raise


@pytest.fixture(scope="session")
def test_engine():
    """Create test database and tables."""
    # Create the test database
    create_test_database()

    # Create engine with no connection pooling
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # Disable connection pooling
        isolation_level="AUTOCOMMIT",  # Allow database operations outside transactions
    )

    try:
        # Create all tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        yield engine

    finally:
        # Cleanup
        try:
            close_all_sessions()

            # Drop all tables
            Base.metadata.drop_all(bind=engine)

            # Dispose of the engine
            engine.dispose()

            # Drop the test database
            if database_exists(TEST_DATABASE_URL):
                drop_database(TEST_DATABASE_URL)
        except Exception as e:
            print(f"Error during cleanup: {e}")


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for a test."""
    # Create a new connection
    connection = test_engine.connect()

    # Begin a non-ORM transaction
    transaction = connection.begin()

    # Create session
    SessionLocal = sessionmaker(bind=connection, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        # Always rollback and close
        try:
            session.close()
        except:
            pass
        try:
            transaction.rollback()
        except:
            pass
        try:
            connection.close()
        except:
            pass


def test_database_connection(db_session):
    """Test that we can connect to the database."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    print("Database connection test passed")


def test_table_creation(db_session):
    """Test that all tables were created."""
    # Get list of all tables
    result = db_session.execute(
        text(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
        )
    )
    tables = [row[0] for row in result]
    print(f"Found tables: {tables}")

    expected_tables = {"property", "pricingrule", "pricehistory", "marketdata"}
    missing_tables = expected_tables - set(tables)
    assert not missing_tables, f"Missing tables: {missing_tables}"


def test_can_create_property(db_session):
    """Test that we can create a property in the database."""
    test_property = Property(
        name="Test Property",
        address="123 Test St",
        square_footage=1000.0,
        bedrooms=2,
        bathrooms=2.0,
        amenities={"parking": True},
        current_price=1500.0,
    )

    db_session.add(test_property)
    db_session.commit()

    result = db_session.query(Property).filter_by(name="Test Property").first()
    assert result is not None
    assert result.address == "123 Test St"
