import os
import sys
import json
import bcrypt 

# Ensure the core application layout sits properly within the executable environment path runtime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User, SecurityEvent
from app.config import settings
from sqlalchemy import inspect, text

print("--- Starting Secure DB Creation & Seeding Script ---")

# 1. ORM Generation Phase: Build relational schemas safely in SQLite persistence layer
Base.metadata.create_all(bind=engine)
print("SUCCESS: Tables verified and created in SQLite storage layer!")

def ensure_event_columns():
    """Add new columns to existing security_events tables without dropping data."""
    inspector = inspect(engine)
    if "security_events" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("security_events")}
    migrations = [
        ("description", "VARCHAR"),
        ("status", "VARCHAR DEFAULT 'Open'"),
        ("comments", "VARCHAR"),
    ]
    with engine.begin() as conn:
        for col_name, col_type in migrations:
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE security_events ADD COLUMN {col_name} {col_type}"))
                print(f"MIGRATION: Added column security_events.{col_name}")

ensure_event_columns()

# Open thread session block to populate starting mock states safely
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
    # Architectural Upgrade: Dynamically fetching verified profiles directly from central config pipeline
    initial_users = settings.INITIAL_USERS
    
    for user_data in initial_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if not existing_user:
            print(f"Seeding initial database account {user_data['id']}: {user_data['email']}...")
            new_user = User(
                id=user_data["id"], 
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"], 
                status=user_data["status"]
            )
            db.add(new_user)
            print(f"SUCCESS: Provisioned '{user_data['email']}' with ID: {user_data['id']}.")
        else:
            print(f"INFO: User profile '{user_data['email']}' already exists in DB. Skipping.")

    # ==========================================
    # PHASE B: MOCK EVENTS DATA EXTRACTION & SYNC
    # ==========================================
    # Resolving path dynamically to load standard contract data from mock_events.json
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    EVENTS_FILE_PATH = os.path.join(_SCRIPT_DIR, "data", "mock_events.json")

    if os.path.exists(EVENTS_FILE_PATH):
        with open(EVENTS_FILE_PATH, "r", encoding="utf-8") as file:
            json_events = json.load(file)
            
        print(f"Syncing {len(json_events)} security events from JSON repository to SQLite...")
        for ev in json_events:
            existing_event = db.query(SecurityEvent).filter(SecurityEvent.id == ev.get("id")).first()
            if not existing_event:
                new_event = SecurityEvent(
                    id=ev.get("id"),
                    severity=ev.get("severity"),
                    title=ev.get("title"),
                    asset=ev.get("assetHostname"),
                    source_ip=ev.get("sourceIp"),
                    timestamp=ev.get("timestamp"),
                    description=ev.get("description", ""),
                    status=ev.get("status", "Open"),
                    comments=ev.get("comments", ""),
                    user_id=ev.get("userId")
                )
                db.add(new_event)
            else:
                # Backfill narrative fields on previously seeded rows
                if not existing_event.description and ev.get("description"):
                    existing_event.description = ev.get("description")
                if not existing_event.status:
                    existing_event.status = ev.get("status", "Open")
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