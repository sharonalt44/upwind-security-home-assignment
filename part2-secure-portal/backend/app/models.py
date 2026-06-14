from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    SQLAlchemy Model representing the 'users' application database table.
    Stores core user profiles, cryptographic credentials, operational roles, and account states.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Operational roles authorized by the access management architecture: "admin", "analyst", "viewer"
    role = Column(String, default="analyst", nullable=False) 
    
    # Explicit account status bounds used for access control mitigation: "active", "disabled"
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
    
    # Operational severity classification matrix: "low", "medium", "high", "critical"
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

    # Classification tags synced from telemetry ingestion pipelines
    tags = Column(JSON, default=list, nullable=False)
    
    # 🛡️ ANTI-BOLA GUARDRAIL: Strict dynamic database binding isolating entries to an explicit profile
    user_id = Column(String, ForeignKey("users.id"), nullable=False)


class BlacklistedToken(Base):
    """
    SQLAlchemy Model representing the 'blacklisted_tokens' validation engine.
    Stores revoked JSON Web Tokens (JWT) upon explicit user logout actions to mitigate session replay attacks.
    """
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)