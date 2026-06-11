import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User

print("--- Starting DB Creation Script ---")
try:
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: 'users.db' file and tables created successfully!")
except Exception as e:
    print(f"ERROR: Could not create database: {e}")