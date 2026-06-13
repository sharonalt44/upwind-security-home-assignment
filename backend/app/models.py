from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    password_hash = Column(String, nullable=False)
    
    # Roles allowed by frontend: "admin", "analyst", "viewer"
    role = Column(String, default="analyst", nullable=False) 
    
    # Statuses allowed by frontend: "active", "disabled"
    status = Column(String, default="active", nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class SecurityEvent(Base):
    """
    SQLAlchemy Model representing the 'security_events' data warehouse.
    Enforces persistent tracking of high-fidelity logs matching the mock environment schema.
    """
    __tablename__ = "security_events"

    # Unique global event identifier mapped from corporate telemetry streams
    id = Column(String, primary_key=True, index=True)
    
    # Operational severity classification matrix: "Low", "Medium", "High", "Critical"
    severity = Column(String, nullable=False)
    
    # Title classification detailing the discovered attack pattern or vector
    title = Column(String, nullable=False)
    
    # Targeted asset tracking metrics specifying infrastructure components or endpoints
    asset = Column(String, nullable=False)
    
    # Malicious source network address context derived from connection state logs
    source_ip = Column(String, nullable=False)
    
    # ISO-standardized timestamp metadata representing the exact detection phase
    timestamp = Column(String, nullable=False)

    # Rich-text incident narrative synced from telemetry ingestion pipelines
    description = Column(String, nullable=True, default="")

    # Operational workflow state: Open, In Progress, Resolved
    status = Column(String, nullable=False, default="Open")

    # Analyst notes and investigation commentary
    comments = Column(String, nullable=True, default="")
    
    # 🛡️ ANTI-BOLA GUARDRAIL: Strict dynamic database binding isolating entries to an explicit profile
    user_id = Column(String, ForeignKey("users.id"), nullable=False)