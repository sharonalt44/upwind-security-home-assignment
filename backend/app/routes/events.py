from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, SecurityEvent
from app.schemas import EventResponse, EventCreate, EventUpdate
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/events",
    tags=["Events Data"]
)

# ==========================================
# 1. READ PERMISSION ENDPOINT - ALL EVENTS (GET)
# ==========================================
@router.get("", response_model=List[EventResponse])
def get_security_events(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Exposes protected security event logs directly from the relational storage engine.
    Enforces Strict Object-Level Authorization (BOLA / IDOR mitigation pipeline):
    - Admins bypass filters entirely, gaining total structural insight over the environment.
    - Analysts and Viewers are confined dynamically to events matching their session profile ID.
    """
    # 👑 Admin Bypass Rule: Full corporate scope oversight
    if current_user.role == "admin":
        return db.query(SecurityEvent).all()
        
    # 🛡️ BOLA Isolation Query: Dynamic context extraction restricting profile leakage 
    return db.query(SecurityEvent).filter(SecurityEvent.user_id == current_user.id).all()


# ==========================================
# 2. READ PERMISSION ENDPOINT - SINGLE EVENT (GET)
# ==========================================
@router.get("/{event_id}", response_model=EventResponse)
def get_single_security_event(
    event_id: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Resolves a specific security incident payload.
    Enforces Object-Level Authorization checking logic to block horizontal privilege 
    escalation if an analyst tries to query an unassigned incident ID.
    """
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Security incident profile not found."
        )

    # 🛡️ BOLA Guardrail: Restrict viewing unless the client is an Admin or the designated resource owner
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not possess authorized clearance to inspect this telemetry instance."
        )
        
    return event


# ==========================================
# 3. WRITE PERMISSION ENDPOINT (POST)
# ==========================================
@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_security_event(event_in: EventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Enforces RBAC verification rules on log ingestion pipelines.
    Rejects actions from non-privileged system connections instantly.
    """
    # 🛑 Access Guardrail: Terminate requests if the validation signature isn't 'admin' 
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Only administrators possess authorized clearance to create new security logs."
        )

    # Validate that the targeted owner profile actually exists and is active before linking records
    owner = db.query(User).filter(
    User.id == event_in.user_id, 
    User.deleted_at.is_(None),
    User.status == "active"
        ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target assignment user_id does not exist or is currently disabled within the identity registry.",
        )
        
    # Instance compilation upon successful validation check
    new_event = SecurityEvent(
        id=event_in.id,
        severity=event_in.severity,
        title=event_in.title,
        asset=event_in.asset,
        source_ip=event_in.source_ip,
        timestamp=event_in.timestamp,
        tags=event_in.tags or [],
        user_id=event_in.user_id # Linking log context explicitly to targeted analyst owner 
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# ==========================================
# 4. PURGE PERMISSION ENDPOINT (DELETE)
# ==========================================
@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_security_event(event_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Protects log tracking indexes from rogue data deletion maneuvers.
    Guarantees strict audit trace retention across operational dashboards.
    """
    # 🛑 Access Guardrail: Prevent rogue operators or compromised tokens from clearing event tracks 
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Only administrators possess authorized clearance to purge active log traces."
        )
        
    # Attempt record resolution across persistence tables
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event profile not found.")
        
    # Execution block if authentication and verification match perfectly
    db.delete(event)
    db.commit()
    return {"message": f"Security log target '{event_id}' has been permanently purged by system administrator."}


# ==========================================
# 5. UPDATE PERMISSION ENDPOINT (PATCH)
# ==========================================
@router.patch("/{event_id}", response_model=EventResponse)
def update_security_event(
    event_id: str, 
    event_in: EventUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Updates operational event metrics dynamically.
    Enforces dual-layer authorization mapping based on user clearance tiers:
    - Admins can locate and modify any structural log field across the database.
    - Analysts are strictly bound via validation check to their assigned identity rows.
    """
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Viewers have read-only access and cannot modify security logs."
        )

    # 👑 Step 1: Resolve the targeted record from the database based on roles
    if current_user.role == "admin":
        # Admins query globally without resource ownership constraints
        event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    else:
        # 🛡️ Analyst BOLA Protection: Query is context-bound strictly to their user_id
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id,
            SecurityEvent.user_id == current_user.id
        ).first()

    # If record execution scope drops empty, intercept and reject immediately
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Security event not found or you are unauthorized to modify this resource."
        )

   # 🔒 Step 2: Evaluate field-level assignment metrics (RBAC Safeguard)
    update_data = event_in.model_dump(exclude_unset=True)
    
    # 🛠️ Empty Payload Validation: Prevent ghost commits to the database
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update."
        )
    
    # Restrict administrative field modifications from falling into analyst requests
    admin_only_fields = {"severity", "user_id", "title", "asset", "source_ip", "tags"}
    if current_user.role != "admin":
        blocked = admin_only_fields.intersection(update_data.keys())
        if blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: Operational analysts cannot modify integrity telemetry fields (severity/assignment/title/asset/source_ip)."
            )

    # Step 3: Apply the allowed changes to the database model instance securely
    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event