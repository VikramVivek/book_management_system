import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..auth import get_current_user, get_password_hash

router = APIRouter()

# Setup logger
logger = logging.getLogger("app.users")


@router.put("/me", response_model=schemas.User, tags=["User Management"])
def update_user_me(
    user_update: schemas.UserCreate,  # You can define a more specific schema if needed
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Update current user's profile information.

    Args:
        user_update (schemas.UserCreate): Data required to update the user profile.
        current_user (schemas.User): The currently authenticated user.
        db (Session): Database session dependency.

    Returns:
        schemas.User: The updated user profile.

    Raises:
        HTTPException: If the user is not found in the database.
    """
    logger.info(f"Updating profile for user ID: {current_user.id}")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if user is None:
        logger.warning(f"User ID: {current_user.id} not found")
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
    logger.info(f"Profile updated successfully for user ID: {current_user.id}")
    return user


@router.get("/me", response_model=schemas.User, tags=["User Management"])
def read_user_me(current_user: schemas.User = Depends(get_current_user)):
    """
    Get current user's profile information.

    Args:
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.User: The current user profile.
    """
    logger.info(f"Fetching profile for user ID: {current_user.id}")
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
    """
    Set or update the current user's preferences.

    Args:
        preferences (schemas.UserPreferencesCreate): The user's preferences to
                                                     set or update.
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.UserPreferences: The updated or newly created user preferences.
    """
    logger.info(f"Setting preferences for user ID: {current_user.id}")
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == current_user.id)
        .first()
    )

    if db_preferences:
        db_preferences.preferred_genres = preferences.preferred_genres
        db_preferences.preferred_authors = preferences.preferred_authors
        logger.info(f"Updated existing preferences for user ID: {current_user.id}")
    else:
        db_preferences = models.UserPreferences(
            **preferences.dict(), user_id=current_user.id
        )
        db.add(db_preferences)
        logger.info(f"Created new preferences for user ID: {current_user.id}")

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
    """
    Get the current user's preferences.

    Args:
        db (Session): Database session dependency.
        current_user (schemas.User): The currently authenticated user.

    Returns:
        schemas.UserPreferences: The user's preferences.

    Raises:
        HTTPException: If no preferences are found for the current user.
    """
    logger.info(f"Fetching preferences for user ID: {current_user.id}")
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == current_user.id)
        .first()
    )

    if not db_preferences:
        logger.warning(f"No preferences found for user ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="User preferences not found")

    return db_preferences
