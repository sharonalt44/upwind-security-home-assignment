import pytest
from fastapi import status
from app.routes.auth import FAILED_ATTEMPTS_TRACKER

def test_register_analyst_success(client):
    """Test that a new analyst can be registered successfully."""
    user_data = {"username": "new_analyst", "password": "SecurePassword123"}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "new_analyst"


def test_register_duplicate_username_fails(client):
    """Test that registering an existing username returns a 400 Bad Request."""
    user_data = {"username": "duplicate_user", "password": "SecurePassword123"}
    # First registration
    client.post("/auth/register", json=user_data)
    # Duplicate attempt
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already registered."


def test_login_success(client):
    """Test successful login and HttpOnly cookie injection."""
    user_data = {"username": "testanalyst", "password": "SecurePassword123"}
    reg_resp = client.post("/auth/register", json=user_data)
    assert reg_resp.status_code == status.HTTP_201_CREATED
    
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Login successful"}
    assert "access_token" in client.cookies


def test_login_invalid_credentials(client):
    """Test that invalid credentials return a generic 401 error."""
    login_data = {"username": "fakeuser", "password": "WrongPassword"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid username or password."


def test_login_brute_force_lockout(client):
    """Test that 5 consecutive failed attempts trigger a 429 lockout."""
    username = "bruteforce_target"
    login_data = {"username": username, "password": "WrongPassword"}
    
    for _ in range(5):
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    lockout_response = client.post("/auth/login", json=login_data)
    assert lockout_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Account is temporarily locked" in lockout_response.json()["detail"]


def test_login_counter_resets_on_success(client):
    """Test that the failed attempts tracker is cleared upon a successful login."""
    username = "reset_user"
    user_credentials = {"username": username, "password": "GoodPassword123"}
    client.post("/auth/register", json=user_credentials)
    
    # Fail 3 times
    for _ in range(3):
        client.post("/auth/login", json={"username": username, "password": "BadPassword"})
        
    assert FAILED_ATTEMPTS_TRACKER[username]["count"] == 3
    
    # Log in successfully with correct credentials
    client.post("/auth/login", json=user_credentials)
    
    # Assert the tracker was successfully wiped for this user
    assert username not in FAILED_ATTEMPTS_TRACKER