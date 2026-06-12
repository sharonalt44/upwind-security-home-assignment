import os
import sys
import bcrypt 

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User
from app.config import settings

print("--- Starting DB Creation & Seeding Script ---")

# 1. Create tables based on the updated models.py schema
Base.metadata.create_all(bind=engine)
print("SUCCESS: Tables created successfully in SQLite database!")

db = SessionLocal()

def hash_password(plain_password: str) -> str:
    """Helper to hash mock passwords securely using bcrypt."""
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

try:
    # Define the core initial users to match Upwind's frontend mock state exactly
    initial_users = [
        {
            "id": "1",
            "email": "admin@penguwave.io",
            "password": "admin123",
            "role": "admin",
            "status": "active"
        },
        {
            "id": "2",
            "email": "analyst@penguwave.io",
            "password": "pass456",
            "role": "analyst",
            "status": "active"
        },
        {
            "id": "3",
            "email": "viewer@penguwave.io",
            "password": "view789",
            "role": "viewer",
            "status": "disabled"  # Mock state defines viewer as disabled initially
        }
    ]

    for user_data in initial_users:
        # Check if user already exists by email
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if not existing_user:
            print(f"Seeding initial {user_data['role']} user: {user_data['email']}...")
            
            new_user = User(
                id=user_data["id"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                status=user_data["status"]
            )
            db.add(new_user)
            print(f"SUCCESS: Created user '{user_data['email']}' with ID: {user_data['id']}")
        else:
            print(f"INFO: User '{user_data['email']}' already exists. Skipping.")
            
    db.commit()
    print("--- Database Seeding Completed Successfully ---")

except Exception as e:
    db.rollback()
    print(f"ERROR: Failed during database seeding context: {e}")
finally:
    db.close()

print("--- DB Setup Script Finished ---")