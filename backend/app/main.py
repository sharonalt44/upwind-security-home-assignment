from fastapi import FastAPI
from app.routes import auth
from app.database import Base, engine  # Informs FastAPI where SQLAlchemy Base and engine are located

# Automatically create all database tables defined in models.py if they do not exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PenguWave - Security Operations Portal",
    description="Secure Backend API for SOC Analyst Management",
    version="1.0.0"
)

# Register the authentication router with the central FastAPI application
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "PenguWave API is up and running"}