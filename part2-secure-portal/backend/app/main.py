from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine

# 🛡️ Updated the import name to match the newer slowapi version framework
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app import models 

Base.metadata.create_all(bind=engine)

# 1. Initialize Limiter first so child routes can safely import it later
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="PenguWave - Security Operations Portal",
    description="Secure Backend API for SOC Analyst Management",
    version="1.0.0"
)

app.state.limiter = limiter
# 🛡️ Updated the exception handler reference
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,                  
    allow_methods=["*"],                     
    allow_headers=["*"],                     
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. The incident has been logged."
        }
    )

@app.get("/")
@limiter.limit("5/minute")
def root(request: Request): 
    return {"status": "healthy", "message": "PenguWave API is up and running"}

# 2. NOW import and include routers after everything else is fully registered
from app.routes import auth, events, users, email_analyzer

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)
app.include_router(email_analyzer.router)