import pytest

# 1. Test successful registration of a new SOC analyst
def test_register_analyst_success(client):
    payload = {
        "username": "test_analyst_1",
        "password": "securePassword123",
        "role": "analyst"
    }
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test_analyst_1"
    assert data["role"] == "analyst"
    assert data["status"] == "approved"
    assert "id" in data
    assert "password" not in data  # Security check: Password must never be returned!

# 2. Test Cyber Security Control: Prevention of duplicate usernames (User Enumeration protection)
def test_register_duplicate_username_fails(client):
    payload = {
        "username": "duplicate_soc_member",
        "password": "password125",
        "role": "analyst"
    }
    
    # First registration attempt (Should succeed)
    response1 = client.post("/auth/register", json=payload)
    assert response1.status_code == 201
    
    # Second registration attempt with the exact same username (Should be blocked)
    response2 = client.post("/auth/register", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Username already registered."

# 3. Test input validation constraints from Pydantic schema (Short password)
def test_register_short_password_validation_fails(client):
    payload = {
        "username": "valid_name",
        "password": "123",  # Invalid: Too short (min_length=6)
        "role": "analyst"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422  # Pydantic validation error