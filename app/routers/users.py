import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..auth import get_current_user, get_password_hash

router = APIRouter()


@router.put("/me", response_model=schemas.User, tags=["User Management"])
def update_user_me(
    user_update: schemas.UserCreate,  # You can define a more specific schema if needed
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Update current user's profile information.
    """
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user fields
    user.email = user_update.email
    user.username = user_update.username if user_update.username else user.username

    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=schemas.User, tags=["User Management"])
def read_user_me(current_user: schemas.User = Depends(get_current_user)):
    """
    Get current user's profile information.
    """
    logging.error("From users.py /me")
    return current_user


@router.post(
    "/preferences/",
    response_model=schemas.UserPreferences,
    tags=["Recommendations", "User Management"],
)
def set_user_preferences(
    preferences: schemas.UserPreferencesCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == current_user.id)
        .first()
    )

    if db_preferences:
        db_preferences.preferred_genres = preferences.preferred_genres
        db_preferences.preferred_authors = preferences.preferred_authors
    else:
        db_preferences = models.UserPreferences(
            **preferences.dict(), user_id=current_user.id
        )
        db.add(db_preferences)

    db.commit()
    db.refresh(db_preferences)
    return db_preferences


@router.get(
    "/preferences/",
    response_model=schemas.UserPreferences,
    tags=["Recommendations", "User Management"],
)
def get_user_preferences(
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == current_user.id)
        .first()
    )

    if not db_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return db_preferences
