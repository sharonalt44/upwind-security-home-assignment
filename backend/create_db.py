import os
import sys
import json
import bcrypt 

# Ensure the core application layout sits properly within the executable environment path runtime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User, SecurityEvent
from app.config import settings

print("--- Starting Secure DB Creation & Seeding Script ---")

# 1. ORM Generation Phase: Build relational schemas safely in SQLite persistence layer [cite: 67]
Base.metadata.create_all(bind=engine)
print("SUCCESS: Tables verified and created in SQLite storage layer!")

# Open thread session block to populate starting mock states safely [cite: 59]
db = SessionLocal()

def hash_password(plain_password: str) -> str:
    """Cryptographic Guardrail: Appends adaptive salt and generates secure Bcrypt hashes."""
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

try:
    # ==========================================
    # PHASE A: INITIAL USERS INJECTION PIPELINE
    # ==========================================
    # Mapping static initial configurations safely by evaluating existing data blocks [cite: 43]
    initial_users = [
        {"id": "usr-001", "email": "admin@penguwave.io", "password": getattr(settings, "USER_001_PASSWORD", "admin123"), "role": "admin", "status": "active"},
        {"id": "usr-002", "email": "analyst@penguwave.io", "password": getattr(settings, "USER_002_PASSWORD", "pass456"), "role": "analyst", "status": "active"},
        {"id": "usr-003", "email": "viewer@penguwave.io", "password": getattr(settings, "USER_003_PASSWORD", "view789"), "role": "viewer", "status": "disabled"}
    ]

    # In-memory tracking set to intercept real-time memory duplication attempts
    seeded_emails = set()
    
    for user_data in initial_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if not existing_user:
            print(f"Seeding initial database account {user_data['id']}: {user_data['email']}...")
            new_user = User(
                id=user_data["id"], 
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]), # Strictly hashing raw text entries [cite: 52]
                role=user_data["role"], 
                status=user_data["status"]
            )
            db.add(new_user)
            seeded_emails.add(user_data["email"])
            print(f"SUCCESS: Provisioned '{user_data['email']}' with ID: {user_data['id']}.")
        else:
            print(f"INFO: User profile '{user_data['email']}' already exists in DB. Skipping.")

    # ==========================================
    # PHASE B: FIRST SUPERUSER FALLBACK ROUTINE
    # ==========================================
    # Safe environment extraction strategy preventing deployment crashes if keys are unmapped
    env_superuser_name = getattr(settings, "FIRST_SUPERUSER_NAME", "admin")
    env_superuser_pass = getattr(settings, "FIRST_SUPERUSER_PASSWORD", "PenguAdmin2026!")
    env_superuser_email = f"{env_superuser_name}@penguwave.io" if "@" not in env_superuser_name else env_superuser_name

    existing_db_user = db.query(User).filter(User.email == env_superuser_email).first()
    if not existing_db_user and env_superuser_email not in seeded_emails:
        print(f"Seeding central enterprise superuser: {env_superuser_email}...")
        env_user = User(
            id="usr-004", 
            email=env_superuser_email, 
            password_hash=hash_password(env_superuser_pass), 
            role="admin", 
            status="active"
        )
        db.add(env_user)

    # ==========================================
    # PHASE C: MOCK EVENTS DATA EXTRACTION & SYNC
    # ==========================================
    # Resolving path dynamically to load standard contract data from mock_events.json [cite: 59]
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    EVENTS_FILE_PATH = os.path.join(_SCRIPT_DIR, "data", "mock_events.json")

    if os.path.exists(EVENTS_FILE_PATH):
        with open(EVENTS_FILE_PATH, "r", encoding="utf-8") as file:
            json_events = json.load(file)
            
        print(f"Syncing {len(json_events)} security events from JSON repository to SQLite...")
        for ev in json_events:
            # Idempotence protection: Prevent runtime crashes by assuring unique record identification
            existing_event = db.query(SecurityEvent).filter(SecurityEvent.id == ev.get("id")).first()
            if not existing_event:
                new_event = SecurityEvent(
                    id=ev.get("id"),
                    severity=ev.get("severity"),
                    title=ev.get("title"),
                    asset=ev.get("assetHostname"),
                    source_ip=ev.get("sourceIp"),
                    timestamp=ev.get("timestamp"),
                    user_id=ev.get("userId") # Binds the record directly to its corresponding owner profile 
                )
                db.add(new_event)
        print("SUCCESS: Events table fully populated and synced!")
    else:
        print("WARNING: mock_events.json file not found. Skipping events seed.")

    # Commit transactions cleanly to disk
    db.commit()
    print("--- Database Seeding Completed Successfully ---")

except Exception as e:
    db.rollback()
    print(f"CRITICAL ERROR: Exception intercepted during environment setup: {e}")
finally:
    db.close()

print("--- Secure DB Setup Script Terminated Cleanly ---")