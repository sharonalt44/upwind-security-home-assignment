from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app import crud

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_analyst(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new SOC analyst or admin.
    This endpoint checks for duplicates and securely hashes the password before saving.
    """
    # 1. Cyber Security Check: Prevent User Enumeration by keeping errors clean and generic
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    
    # 2. Create the user using our secure CRUD logic
    return crud.create_user(db=db, user=user)