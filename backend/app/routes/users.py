from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Fetches all active accounts from the centralized database layer.
    Enforces full admin authentication and filtering.
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
    Updates a user's role or status. Prevents admins from disabling their own account.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided.",
        )

    if user_id == current_user.id and update_data.get("status") == "disabled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account.",
        )

    if update_data.get("status") not in (None, "active", "disabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'active' or 'disabled'.",
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

@router.delete("/delete/{user_id}", response_model=dict)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Hard Delete Mechanism: Completely purges a target user record from the system.
    Includes an intentional self-deletion prevention check to avoid complete lockout.
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
            detail="User not found."
        )
        
    # Performs a permanent database purge to satisfy the hard delete requirement
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}