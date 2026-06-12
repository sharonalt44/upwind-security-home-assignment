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