import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import EventResponse
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(
    prefix="/events",
    tags=["Events Data"]
)

# Resolve backend/data/events.json from this file's location (app/routes/events.py)
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_FILE_PATH = os.path.join(_BACKEND_ROOT, "data", "mock_events.json")

@router.get("/", response_model=List[EventResponse])
def get_security_events(current_user: User = Depends(get_current_user)):
    """
    Exposes protected security event data from the local JSON repository.
    Only accessible by authenticated and approved analysts.
    """
    # 🛡️ Access Control: The Depends guard blocks unauthenticated users from reaching this block
    
    print(f"Reading events file from: {EVENTS_FILE_PATH}")

    # Verify the JSON repository exists on disk
    if not os.path.exists(EVENTS_FILE_PATH):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: Security events data file missing."
        )
        
    try:
        with open(EVENTS_FILE_PATH, "r", encoding="utf-8") as file:
            events_data = json.load(file)
        return events_data
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: Failed to parse events repository."
        )