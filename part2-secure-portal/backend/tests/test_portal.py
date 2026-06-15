import pytest
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool 
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import User 
from app.main import app
from app.routes.auth import FAILED_ATTEMPTS_TRACKER

# ==============================================================================
# 🏗️ TEST ENVIRONMENT SETUP (Isolated In-Memory SQLite Architecture)
# ==============================================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Reuses the same connection pool so tables don't vanish
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Fixture to handle database creation and lifecycle per test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture to override the production dependency with the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_client(client, db_session):
    """Authenticated admin session for protected admin-only endpoints."""
    from app.schemas import UserCreate
    from app import crud

    crud.create_user(
        db_session,
        UserCreate(email="admin@test.io", password="AdminPass123!", role="admin"),
    )
    login_resp = client.post(
        "/auth/login",
        json={"email": "admin@test.io", "password": "AdminPass123!"},
    )
    assert login_resp.status_code == 200
    return client

@pytest.fixture(autouse=True)
def reset_failed_attempts_tracker():
    """Autouse fixture to completely clear the Brute-Force tracker to prevent cross-pollution."""
    from app.routes.auth import FAILED_ATTEMPTS_TRACKER
    FAILED_ATTEMPTS_TRACKER.clear()
    yield
    FAILED_ATTEMPTS_TRACKER.clear()


# ==============================================================================
# 🛡️ MODULE 1: AUTHENTICATION & ACCESS CONTROL TESTS
# ==============================================================================

def test_register_analyst_success(admin_client):
    """Test that an admin can register a new user successfully."""
    user_data = {"email": "new_analyst@penguwave.io", "password": "SecurePassword123"}
    response = admin_client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "new_analyst@penguwave.io"

def test_register_unauthenticated_fails(client):
    """Test that unauthenticated registration attempts are blocked."""
    user_data = {"email": "intruder@penguwave.io", "password": "SecurePassword123"}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_duplicate_email_fails(admin_client):
    """Test that registering an existing email returns a 400 Bad Request."""
    user_data = {"email": "duplicate_user@penguwave.io", "password": "SecurePassword123"}
    admin_client.post("/auth/register", json=user_data)
    response = admin_client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered."

def test_login_success(admin_client):
    """Test successful login, HttpOnly cookie injection, and user object body return."""
    user_data = {"email": "testanalyst@penguwave.io", "password": "SecurePassword123"}
    reg_resp = admin_client.post("/auth/register", json=user_data)
    assert reg_resp.status_code == status.HTTP_201_CREATED

    response = admin_client.post("/auth/login", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "testanalyst@penguwave.io"
    assert "access_token" in admin_client.cookies

def test_login_invalid_credentials(client):
    """Test that invalid credentials return a generic 401 error."""
    login_data = {"email": "fakeuser@penguwave.io", "password": "WrongPassword"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password."

def test_register_user_with_string_timestamp_id(admin_client):
    """Test backend generates and stores a string timestamp ID correctly upon registration."""
    user_data = {"email": "react_user@penguwave.io", "password": "SecurePassword123"}
    response = admin_client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    returned_id = response.json()["id"]
    assert isinstance(returned_id, str)
    assert len(returned_id) >= 10


# ==============================================================================
# 🛡️ MODULE 2: THREAT MITIGATION (BRUTE-FORCE & BOLA/IDOR) TESTS
# ==============================================================================

def test_login_brute_force_lockout(client):
    """Test that 5 consecutive failed attempts on an email account trigger a 429 lockout."""
    email = "bruteforce_target@penguwave.io"
    login_data = {"email": email, "password": "WrongPassword"}

    for _ in range(5):
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    lockout_response = client.post("/auth/login", json=login_data)
    assert lockout_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Too many failed login attempts" in lockout_response.json()["detail"]

def test_login_counter_resets_on_success(admin_client):
    """Test that the failed attempts tracker is cleared upon a successful login."""
    email = "reset_user@penguwave.io"
    user_credentials = {"email": email, "password": "GoodPassword123"}
    admin_client.post("/auth/register", json=user_credentials)

    for _ in range(3):
        admin_client.post("/auth/login", json={"email": email, "password": "BadPassword"})

    assert FAILED_ATTEMPTS_TRACKER[email]["count"] == 3
    admin_client.post("/auth/login", json=user_credentials)
    assert email not in FAILED_ATTEMPTS_TRACKER

def test_get_events_authenticated_analyst_success(admin_client):
    """Test authenticated analyst can access the events endpoint successfully."""
    user_credentials = {"email": "analyst@penguwave.io", "password": "SecurePassword123"}
    admin_client.post("/auth/register", json=user_credentials)
    admin_client.post("/auth/login", json=user_credentials)

    response = admin_client.get("/events")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_events_bola_mitigation_for_new_user(admin_client):
    """Test BOLA: A newly registered user with a generated ID is isolated and gets empty telemetry."""
    user_credentials = {"email": "new_guy@penguwave.io", "password": "SecurePassword123"}
    admin_client.post("/auth/register", json=user_credentials)
    admin_client.post("/auth/login", json=user_credentials)

    response = admin_client.get("/events")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_events_unauthenticated_fails(client):
    """Test Security Guardrail: Unauthenticated requests to /events are blocked."""
    response = client.get("/events")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]


# ==============================================================================
# 🛡️ MODULE 3: RATE LIMITING (ANTI-DOS FLIP BREAKER) TEST
# ==============================================================================

def test_api_rate_limiting_gatekeeper(client):
    """
    🎯 Threat Vector: API Flooding / Resource Exhaustion (DoS)
    Validates that the server active limiter (SlowAPI) intercepts rapid bursts on the root route.
    """
    triggered_limits = False
    
    # Trigger an intentional flooding sequence of 10 rapid iterations on the root endpoint (/)
    for _ in range(10):
        response = client.get("/")
        if response.status_code == 429:
            triggered_limits = True
            break
            
    assert triggered_limits is True