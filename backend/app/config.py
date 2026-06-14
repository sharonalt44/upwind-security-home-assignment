import os
import sys
from pydantic import ConfigDict, ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    DATABASE_URL: str
    JWT_SECRET_KEY: str

   
    USER_001_EMAIL: str | None = None
    USER_001_PASSWORD: str | None = None

    USER_002_EMAIL: str | None = None
    USER_002_PASSWORD: str | None = None

    USER_003_EMAIL: str | None = None
    USER_003_PASSWORD: str | None = None

    @property
    def INITIAL_USERS(self) -> list[dict[str, str]]:
        """
        Dynamically evaluate, validate, and bundle the starting system profiles.
        If a user is missing either their email or password in the .env, 
        they are safely excluded from the pipeline to prevent invalid accounts.
        """
        raw_profiles = [
            {
                "id": "usr-001", 
                "email": self.USER_001_EMAIL, 
                "password": self.USER_001_PASSWORD,
                "role": "admin", 
                "status": "active"
            },
            {
                "id": "usr-002", 
                "email": self.USER_002_EMAIL, 
                "password": self.USER_002_PASSWORD,
                "role": "analyst", 
                "status": "active"
            },
            {
                "id": "usr-003", 
                "email": self.USER_003_EMAIL, 
                "password": self.USER_003_PASSWORD,
                "role": "viewer", 
                "status": "disabled"
            }
        ]

        return [p for p in raw_profiles if p["email"] and p["password"]]

   
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_FAILED_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    COOKIE_SECURE: bool = False
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        extra="ignore",
        case_sensitive=False
    )


try:
    settings = Settings()
except ValidationError as e:
    print("\n" + "="*60, file=sys.stderr)
    print("❌ CRITICAL CONFIGURATION ERROR: Server Startup Aborted.", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("Missing or invalid infrastructure variables in your local '.env' file.", file=sys.stderr)
    print("Please verify that both 'DATABASE_URL' and 'JWT_SECRET_KEY' are properly defined.", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    
    
    sys.exit(1)