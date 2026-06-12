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
    Enforces Strict Object-Level Authorization (BOLA/IDOR protection):
    - Admins bypass filters and view all global logs.
    - Analysts and Viewers are strictly isolated to their matching mock userId mapping.
    """
    # Verify the JSON repository exists on disk
    if not os.path.exists(EVENTS_FILE_PATH):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: Security events data file missing."
        )
        
    try:
        with open(EVENTS_FILE_PATH, "r", encoding="utf-8") as file:
            all_events = json.load(file)
            
        # 👑 1. Admin bypass: Global visibility across the entire corporate perimeter
        if current_user.role == "admin":
            return all_events
            
        # 🛡️ 2. Analyst / Viewer dynamic isolation based on their persistent database ID string
        # Maps user.id "2" to "usr-002", and user.id "3" to "usr-003"
        expected_json_uid = f"usr-00{current_user.id}"
        
        filtered_events = [
            event for event in all_events 
            if event.get("userId") == expected_json_uid
        ]
        
        return filtered_events

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: Failed to parse events repository."
        )