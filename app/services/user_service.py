import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas

# Set up logger
logger = logging.getLogger("app.user_service")


def fetch_user_preferences(db: Session, user_id: int) -> schemas.UserPreferences:
    """
    Fetch the user preferences for a given user ID.

    Args:
        db (Session): SQLAlchemy session to interact with the database.
        user_id (int): ID of the user whose preferences are being fetched.

    Returns:
        schemas.UserPreferences: The user preferences schema object.

    Raises:
        HTTPException: If the user or user preferences are not found.
    """
    logger.info(f"Fetching user preferences for user_id: {user_id}")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.error(f"User not found for user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == user_id)
        .first()
    )
    if not preferences:
        logger.error(f"User preferences not found for user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User preferences not found")

    logger.info(f"User preferences fetched successfully for user_id: {user_id}")
    return schemas.UserPreferences.from_orm(preferences)
