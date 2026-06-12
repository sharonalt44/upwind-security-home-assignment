import pytest
from fastapi import status
from app.routes.auth import FAILED_ATTEMPTS_TRACKER

def test_register_analyst_success(client):
    """Test that a new analyst can be registered successfully using an email identifier."""
    user_data = {"email": "new_analyst@penguwave.io", "password": "SecurePassword123"}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "new_analyst@penguwave.io"


def test_register_duplicate_email_fails(client):
    """Test that registering an existing email returns a 400 Bad Request."""
    user_data = {"email": "duplicate_user@penguwave.io", "password": "SecurePassword123"}
    # First registration
    client.post("/auth/register", json=user_data)
    # Duplicate attempt
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered."


def test_login_success(client):
    """Test successful login, HttpOnly cookie injection, and user object body return."""
    user_data = {"email": "testanalyst@penguwave.io", "password": "SecurePassword123"}
    reg_resp = client.post("/auth/register", json=user_data)
    assert reg_resp.status_code == status.HTTP_201_CREATED
    
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    
    # 🔄 Updated assertion: Frontend expects the user profile payload on successful login
    assert response.json()["email"] == "testanalyst@penguwave.io"
    assert "access_token" in client.cookies


def test_login_invalid_credentials(client):
    """Test that invalid credentials return a generic 401 error mapping to the email schema."""
    login_data = {"email": "fakeuser@penguwave.io", "password": "WrongPassword"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password."


def test_login_brute_force_lockout(client):
    """Test that 5 consecutive failed attempts on an email account trigger a 429 lockout."""
    email = "bruteforce_target@penguwave.io"
    login_data = {"email": email, "password": "WrongPassword"}
    
    for _ in range(5):
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    lockout_response = client.post("/auth/login", json=login_data)
    assert lockout_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Account is temporarily locked" in lockout_response.json()["detail"]


def test_login_counter_resets_on_success(client):
    """Test that the failed attempts tracker is cleared upon a successful login."""
    email = "reset_user@penguwave.io"
    user_credentials = {"email": email, "password": "GoodPassword123"}
    client.post("/auth/register", json=user_credentials)
    
    # Fail 3 times
    for _ in range(3):
        client.post("/auth/login", json={"email": email, "password": "BadPassword"})
        
    assert FAILED_ATTEMPTS_TRACKER[email]["count"] == 3
    
    # Log in successfully with correct credentials
    client.post("/auth/login", json=user_credentials)
    
    # Assert the tracker was successfully wiped for this user email registry
    assert email not in FAILED_ATTEMPTS_TRACKER



def test_register_user_with_string_timestamp_id(client):
    """Test Mission 4: Verify backend generates and stores a string timestamp ID correctly upon registration."""
    user_data = {
        "email": "react_user@penguwave.io",
        "password": "SecurePassword123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify the backend generated an active, dynamic string representation of a timestamp id
    returned_id = response.json()["id"]
    assert isinstance(returned_id, str)
    assert len(returned_id) >= 10  # Confirms it is a long timestamp string


def test_get_events_authenticated_analyst_success(client, db_session):
    """Test Mission 5: Authenticated analyst with base system ID '2' can view their own telemetry events (usr-002)."""
    from app.models import User

    # 1. Register normally via the API router to handle all password hashing internally
    user_credentials = {"email": "analyst@penguwave.io", "password": "SecurePassword123"}
    client.post("/auth/register", json=user_credentials)
    
    # 2. Force change the generated ID to "2" in the DB to align with mock_events.json seed state
    analyst_user = db_session.query(User).filter_by(email="analyst@penguwave.io").first()
    analyst_user.id = "2"
    db_session.commit()

    # 3. Log in with the registered credentials to set the HttpOnly cookie session
    client.post("/auth/login", json=user_credentials)

    # 4. Query the events endpoint
    response = client.get("/events")
    assert response.status_code == status.HTTP_200_OK
    
    # 5. Assert that the list is populated and every event belongs strictly to usr-002
    events = response.json()
    assert len(events) > 0
    for event in events:
        assert event["userId"] == "usr-002"


def test_get_events_bola_mitigation_for_new_user(client):
    """Test Mission 5 (BOLA): A newly registered user with a generated ID is isolated and gets empty telemetry."""
    user_credentials = {"email": "new_guy@penguwave.io", "password": "SecurePassword123"}
    client.post("/auth/register", json=user_credentials)
    client.post("/auth/login", json=user_credentials)

    # Query the events endpoint
    response = client.get("/events")
    assert response.status_code == status.HTTP_200_OK
    
    # BOLA enforcement: Returns empty list because their dynamic string ID prefix has no matched mock data
    assert response.json() == []


def test_get_events_unauthenticated_fails(client):
    """Test Security Guardrail: Unauthenticated requests to /events are blocked with precise error messaging."""
    response = client.get("/events")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # 🔄 Updated to match your backend's exact custom error string
    assert response.json()["detail"] == "Not authenticated. Access token missing."