import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Set testing environment
os.environ["TESTING"] = "1"

# Import after setting TESTING environment
from app.main import app
from app.core.database import get_db
from .test_db import test_engine, db_session  # Import fixtures from test_db.py


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def override_get_db(db_session: Session) -> Generator:
    """
    Override the get_db dependency for testing.
    This ensures tests use the test database session.
    """

    def override_db():
        try:
            yield db_session
        finally:
            pass  # Session handling is done by the db_session fixture

    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()
