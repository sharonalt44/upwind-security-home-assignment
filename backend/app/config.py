import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    

    # 🔑 Seed passcodes mapped to satisfy Pydantic strict parsing
    USER_001_PASSWORD: str = "admin123"
    USER_002_PASSWORD: str = "pass456"
    USER_003_PASSWORD: str = "view789"

    # 👥 Dynamic Initial Users Registry Pipeline
    @property
    def INITIAL_USERS(self) -> list[dict[str, str]]:
        """
        Dynamically evaluate and bundle the starting system profiles.
        You can easily add, remove, or modify users in this list.
        """
        return [
            {
                "id": "usr-001", 
                "email": "admin@penguwave.io", 
                "password": self.USER_001_PASSWORD, 
                "role": "admin", 
                "status": "active"
            },
            {
                "id": "usr-002", 
                "email": "analyst@penguwave.io", 
                "password": self.USER_002_PASSWORD, 
                "role": "analyst", 
                "status": "active"
            },
            {
                "id": "usr-003", 
                "email": "viewer@penguwave.io", 
                "password": self.USER_003_PASSWORD, 
                "role": "viewer", 
                "status": "disabled"
            }
            # To add a new user in the future, just drop a new dict right here:
            # {
            #     "id": "usr-004",
            #     "email": "new_analyst@penguwave.io",
            #     "password": "TemporaryPassword123!",
            #     "role": "analyst",
            #     "status": "active"
            # }
        ]

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_FAILED_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # 🛡️ Architectural Configuration
    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        extra="ignore",          # Safely bypass any unexpected configuration entries
        case_sensitive=False     # Neutralize casing mismatches dynamically
    )

settings = Settings()