from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.schemas import UserResponse, UserUpdate, UserCreate
from app import crud

router = APIRouter(prefix="/users", tags=["Users"])

ALLOWED_ROLES = frozenset({"admin", "analyst", "viewer"})
ALLOWED_STATUSES = frozenset({"active", "disabled"})


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Administrative creation of a new user profile.
    Validates email uniqueness and provisions the account via the CRUD layer.
    """
    existing_user = crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        if existing_user.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database conflict: Email already registered.",
            )
        
        existing_user.deleted_at = None
        existing_user.role = user_in.role
        existing_user.status = user_in.status
        existing_user.password_hash = crud.hash_password(user_in.password)
        
        db.commit()
        db.refresh(existing_user)
        return existing_user

    return crud.create_user(db=db, user=user_in)


@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Returns all non-deleted user accounts.
    Requires an authenticated admin session.
    """
    return db.query(User).filter(User.deleted_at.is_(None)).all()


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Partially updates a user's role and/or status.
    Prevents admins from disabling or reassigning their own account.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided.",
        )

    if user_id == current_user.id:
        if update_data.get("status") == "disabled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable your own account.",
            )
        if "role" in update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role.",
            )

    if "status" in update_data and update_data["status"] not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'active' or 'disabled'.",
        )

    if "role" in update_data and update_data["role"] not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin', 'analyst', or 'viewer'.",
        )

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Permanently removes a user record from the system.
    Self-deletion is blocked to prevent administrative lockout.
    Deletion is permitted regardless of account status.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account.",
        )

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "User deleted successfully"}