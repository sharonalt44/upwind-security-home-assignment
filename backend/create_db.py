import os
import sys
import json

# Ensure the core application layout sits properly within the executable environment path runtime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.config import settings
except Exception as e:
    print("\n" + "="*60)
    print(" ❌ [CRITICAL CONFIGURATION ERROR] ENVIRONMENT INITIALIZATION FAILED")
    print("="*60)
    print("The bootstrap setup script cannot safely initialize the application layers.")
    print("Reason: Missing or invalid security configuration inside '.env'.")
    print("\n📢 REMEDIATION ACTION REQUIRED:")
    print("  1. Ensure your local '.env' file exists in the secure root directory.")
    print("  2. Verify that at least one administrative profile password is fully defined.")
    print("  3. Confirm that core system variables (DATABASE_URL, JWT_SECRET_KEY) are populated.")
    print("="*60 + "\n")
    sys.exit(1)

from app.database import engine, Base, SessionLocal
from app.models import User, SecurityEvent
from app.crud import hash_password
from sqlalchemy import inspect, text

print("\n" + "="*60)
print(" 🐧 PENGUWAVE SYSTEM INTEGRITY & REGISTRY BOOTSTRAP 🐧")
print("="*60)

# Build relational schemas safely in SQLite persistence layer
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
        ("tags", "JSON DEFAULT '[]'"),
    ]
    with engine.begin() as conn:
        for col_name, col_type in migrations:
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE security_events ADD COLUMN {col_name} {col_type}"))
                print(f"MIGRATION: Added column security_events.{col_name}")

ensure_event_columns()

# Open thread session block to populate starting mock states safely
db = SessionLocal()

successful_seeds = []
failed_seeds_missing_env = []
skipped_seeds_already_exists = []

try:
    # ==========================================
    # PHASE A: INITIAL USERS INJECTION PIPELINE
    # ==========================================
    initial_users = settings.INITIAL_USERS
    
    # Enforce administrative boundaries
    defined_admins = [u for u in initial_users if u.get("role") == "admin"]
    if not defined_admins:
        print("\n❌ [CRITICAL CONFIGURATION ERROR] Bootstrap pipeline aborted.")
        print("   Reason: No valid administrative profiles successfully loaded from .env Configuration.")
        print("   Remediation: Please ensure USER_001_EMAIL and USER_001_PASSWORD are set in your .env file.")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Secure string validation parsing for administrator safeguards
    valid_admins_with_passwords = [
        u for u in defined_admins 
        if u.get("password") and isinstance(u["password"], str) and u["password"].strip()
    ]
    if not valid_admins_with_passwords:
        print("\n❌ [CRITICAL SECURITY FAILURE] Bootstrap pipeline aborted.")
        print("   Reason: Zero administrative accounts possess a valid password string in the environment.")
        print("   Impact: System build blocked to prevent permanent admin lockout state.")
        print("="*60 + "\n")
        sys.exit(1)
        
    for user_data in initial_users:
        user_pass = user_data.get("password")
        user_email = user_data.get("email")
        
        # Verify schema payload integrity explicitly
        if not user_pass or not isinstance(user_pass, str) or not user_pass.strip() or not user_email:
            failed_seeds_missing_env.append(user_data)
            continue

        # Hardened Idempotency Check: Verify BOTH ID and Email to prevent Primary Key conflicts on metadata changes
        existing_user = db.query(User).filter(
            (User.email == user_email) | (User.id == user_data["id"])
        ).first()
        
        if not existing_user:
            print(f"Seeding initial database account {user_data['id']}: {user_email}...")
            new_user = User(
                id=user_data["id"], 
                email=user_email,
                password_hash=hash_password(user_pass),
                role=user_data["role"], 
                status=user_data["status"]
            )
            db.add(new_user)
            successful_seeds.append(user_data)
        else:
            actual_email = existing_user.email
            print(f"INFO: User profile '{user_data['id']}' ({actual_email}) already preserved in DB. Skipping.")
            skipped_seeds_already_exists.append(user_data)

    # ==========================================
    # PHASE B: MOCK EVENTS DATA EXTRACTION & SYNC
    # ==========================================
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    EVENTS_FILE_PATH = os.path.join(_SCRIPT_DIR, "data", "mock_events.json")

    if os.path.exists(EVENTS_FILE_PATH):
        with open(EVENTS_FILE_PATH, "r", encoding="utf-8") as file:
            json_events = json.load(file)
            
        print(f"Syncing {len(json_events)} telemetry logs from JSON registry to SQLite...")
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
                    tags=ev.get("tags", []),
                    user_id=ev.get("userId")
                )
                db.add(new_event)
            else:
                if not existing_event.description and ev.get("description"):
                    existing_event.description = ev.get("description")
                if not existing_event.status:
                    existing_event.status = ev.get("status", "Open")
                if not existing_event.tags and ev.get("tags"):
                    existing_event.tags = ev.get("tags", [])
        print("SUCCESS: Security telemetry engine sync finalized.")
    else:
        print("WARNING: mock_events.json contract repository target not found. Skipping phase.")

    # Commit transactions cleanly to disk
    db.commit()

    # ==========================================
    # PHASE C: SYSTEM GENESIS AUDIT SUMMARY REPORT
    # ==========================================
    print("\n" + "="*60)
    print(" 📊 PENGUWAVE DEPLOYMENT & REGISTRY STATUS REPORT ")
    print("="*60)
    
    print(f"✅ Successfully Provisioned Accounts: {len(successful_seeds)}")
    for u in successful_seeds:
        print(f"   [+] Identity: {u['id']} | Role: {u['role']:<7} | Email: {u['email']}")
        
    print(f"ℹ️  Active DB Profiles Preserved (Skipped): {len(skipped_seeds_already_exists)}")
    for u in skipped_seeds_already_exists:
        print(f"   [•] Identity: {u['id']} | Email: {u.get('email')}")

    if failed_seeds_missing_env:
        print("\n⚠️  [SECURITY WARNING] THE FOLLOWING REGISTERED PROFILES WERE BLOCKED:")
        print("   Reason: Missing cryptographic passcodes or emails in deployment runtime environment (.env)")
        for u in failed_seeds_missing_env:
            u_id = u.get('id', 'unknown')
            u_role = u.get('role', 'unknown')
            u_email = u.get('email', 'UNKNOWN')
            print(f"   [-] Identity: {u_id} | Role: {u_role:<7} | Email: {u_email} -> [STATUS: NOT PROVISIONED]")
        print("\n📢 REMEDIATION ACTION REQUIRED:")
        print("   These accounts were omitted to prevent unauthenticated database entry injection.")
        print("   Please contact an active system Administrator to provision them manually")
        print("   via the Secure User Management Dashboard UI components.")
    else:
        print("\n🔒 Identity Registry Integrity: All starting node connections established successfully.")
    
    print("="*60 + "\n")
    print("--- Database Seeding Completed Successfully ---")

except Exception:
    db.rollback()
    print("\n" + "="*60, file=sys.stderr)
    print("❌ [CRITICAL SYSTEM FAULT] Database bootstrapping execution pipeline failed.", file=sys.stderr)
    print("============================================================", file=sys.stderr)
    print("Reason: Integrity constraint violation or corrupted entity schemas dynamically intercepted.", file=sys.stderr)
    print("Execution pipeline rolled back safely. Aborting setup.", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    sys.exit(1)
finally:
    db.close()

print("--- Secure DB Setup Script Terminated Cleanly ---")