import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # CRITICAL: Forces SQLite to share the same in-memory DB across connections
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import User  # Registers the User model mapping before running create_all
from app.main import app

# Setup an isolated, in-memory SQLite database for test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Reuses the same connection pool so tables don't vanish
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to handle database creation and lifecycle per test
@pytest.fixture(scope="function")
def db_session():
    # Create tables in the shared in-memory test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after the test finishes to ensure clean state
        Base.metadata.drop_all(bind=engine)

# Fixture to override the production dependency with the test database session
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    # Inject the override into the FastAPI application
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides after test complete
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def reset_failed_attempts_tracker():
    """
    Autouse fixture to completely clear the Brute-Force tracker before and after each test.
    This prevents test cross-pollution and flaky failures.
    """
    from app.routes.auth import FAILED_ATTEMPTS_TRACKER
    FAILED_ATTEMPTS_TRACKER.clear()
    yield
    FAILED_ATTEMPTS_TRACKER.clear()