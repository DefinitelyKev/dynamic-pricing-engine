import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists, create_database, drop_database

# Set testing environment
os.environ["TESTING"] = "1"

# Import after setting TESTING environment
from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base

# Test database URL
TEST_DATABASE_URL = f"{settings.DATABASE_URL}_test"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database and return engine."""
    # Create the test database if it doesn't exist
    if not database_exists(TEST_DATABASE_URL):
        create_database(TEST_DATABASE_URL)

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
        close_all_sessions()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if database_exists(TEST_DATABASE_URL):
            drop_database(TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()

    # Create session bound to the connection
    TestingSessionLocal = sessionmaker(bind=connection, expire_on_commit=False)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Create a FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def override_get_db(db_session: Session) -> Generator[None, None, None]:
    """
    Override the get_db dependency for testing.
    This ensures tests use the test database session.
    """

    def override_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup is handled by db_session fixture

    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()
