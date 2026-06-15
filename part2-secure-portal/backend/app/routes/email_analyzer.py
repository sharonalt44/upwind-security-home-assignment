from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import httpx 
import re
import uuid

from app.database import get_db
from app.models import SecurityEvent, User

router = APIRouter(prefix="/api/v1/addon", tags=["Gmail Addon"])

class EmailAnalysisRequest(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str

async def get_domain_creation_year(domain: str) -> int:
    """
    Queries the public RDAP (Registry Data Access Protocol) to fetch the creation year of a domain.
    This is a real, free, external Threat Intelligence enrichment step.
    """
    try:
        url = f"https://rdap.org/domain/{domain}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                for event in events:
                    if event.get("eventAction") in ["registration", "creation"]:
                        event_date = event.get("eventDate", "")
                        if event_date:

                            return int(event_date.split("-")[0])
    except Exception:
        pass
    return None  

@router.post("/analyze")
async def analyze_email(request: EmailAnalysisRequest, db: Session = Depends(get_db)):
    score = 0
    signals = []

    suspicious_patterns = [
        r"urgent", r"verify.*account", r"password.*reset", 
        r"bank", r"invoice", r"immediate.*action", r"login.*here"
    ]
    combined_text = (request.subject + " " + request.body).lower()
    matches = sum(1 for pattern in suspicious_patterns if re.search(pattern, combined_text))
            
    if matches > 0:
        weight = min(matches * 20, 50)
        score += weight
        signals.append(f"🚨 Found phishing/urgency language patterns (Weight: {weight}%).")

    sender_lower = request.sender.lower()
    domain = sender_lower.split("@")[-1] if "@" in sender_lower else ""
    
    if domain and domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
        creation_year = await get_domain_creation_year(domain)
        
        if creation_year:
            current_year = datetime.now().year
            domain_age_years = current_year - creation_year
            
            if domain_age_years <= 3:
                score += 25
                signals.append(f"🌐 External Intel Enrichment: Domain '{domain}' is relatively new (Created: {creation_year}, Age: {domain_age_years} years). High spoofing potential.")
            else:
                signals.append(f"🌐 External Intel Enrichment: Domain '{domain}' verified as established (Created: {creation_year}).")
        else:
            signals.append(f"ℹ️ External Intel: Domain '{domain}' registration data could not be retrieved.")

    score = min(score, 100)
    
    verdict = "SAFE"
    color = "#2e7d32"
    if score >= 75:
        verdict = "MALICIOUS"
        color = "#c62828"
    elif score >= 35:
        verdict = "SUSPICIOUS"
        color = "#ef6c00"

    assigned_user_id = "usr-unidentified"
    user_context_signal = "⚠️ Target User: Unidentified Account"

    if score >= 35:
        target_user = db.query(User).filter(User.email == request.recipient.strip()).first()
        if target_user:
            assigned_user_id = target_user.id
            user_context_signal = f"👤 Target User Resolved: {target_user.username}"
        else:
            user_context_signal = f"⚠️ Target User: Unidentified mailbox ({request.recipient})"

        new_incident = SecurityEvent(
            id=f"evt-{str(uuid.uuid4())[:8]}",
            severity="HIGH" if score >= 75 else "MEDIUM",
            title=f"Phishing Alert: {request.subject[:30]}...",
            asset="Gmail-Workspace-Sensor", 
            source_ip="192.0.2.1",
            timestamp=datetime.utcnow().isoformat() + "Z",
            description=f"Recipient: {request.recipient} | Sender: {request.sender} | Risk Score: {score}% | Context: {user_context_signal} | Signals: {', '.join(signals)}",
            status="OPEN",
            comments="",
            tags="[\"phishing\", \"external-intel\"]", 
            user_id=assigned_user_id
        )
        db.add(new_incident)
        db.commit()

    return {
        "score": score,
        "verdict": verdict,
        "color": color,
        "signals": signals,
        "resolved_target": assigned_user_id
    }