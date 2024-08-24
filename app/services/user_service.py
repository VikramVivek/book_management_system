from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas


def fetch_user_preferences(db: Session, user_id: int) -> schemas.UserPreferences:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == user_id)
        .first()
    )
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return schemas.UserPreferences.from_orm(preferences)
