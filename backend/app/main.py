from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import auth, events, users

# 🛡️ Architectural Safeguard: Explicitly import models to register them on the Base metadata
# This ensures SQLAlchemy discovers and compiles the new 'security_events' table flawlessly.
from app import models 

# Automatically create all database tables defined in models.py if they do not exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PenguWave - Security Operations Portal",
    description="Secure Backend API for SOC Analyst Management",
    version="1.0.0"
)

# 🛡️ Security Guardrail: Configure CORS Middleware to allow secure cross-origin browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend development server origin
    allow_credentials=True,                  # Crucial for transmitting secure HttpOnly session cookies
    allow_methods=["*"],                     # Allows standard REST methods (GET, POST, PATCH, DELETE, etc.)
    allow_headers=["*"],                     # Allows all standard request headers
)

# Register all decoupled application routers with the central FastAPI core instance
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "PenguWave API is up and running"}