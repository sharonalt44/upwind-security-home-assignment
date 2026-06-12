import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt 
from app.database import engine, Base, SessionLocal
from app.models import User
from app.config import settings

print("--- Starting DB Creation & Seeding Script ---")


Base.metadata.create_all(bind=engine)
print("SUCCESS: Tables created successfully!")


db = SessionLocal()
try:
    existing_user = db.query(User).filter(User.username == settings.FIRST_SUPERUSER_NAME).first()
    
    if not existing_user:
        print(f"Creating initial admin user: {settings.FIRST_SUPERUSER_NAME}...")
        
        password_bytes = settings.FIRST_SUPERUSER_PASSWORD.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        admin_user = User(
            username=settings.FIRST_SUPERUSER_NAME,
            password_hash=hashed_password,
            role="admin",
            status="approved"
        )
        db.add(admin_user)
        db.commit()
        print(f"SUCCESS: Admin user '{settings.FIRST_SUPERUSER_NAME}' created successfully!")
    else:
        print(f"INFO: Admin user '{settings.FIRST_SUPERUSER_NAME}' already exists.")
except Exception as e:
    db.rollback()
    print(f"ERROR: Failed to create initial user: {e}")
finally:
    db.close()

print("--- DB Setup Script Finished ---")