from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.user_service import fetch_user_preferences

from .. import database
from ..services.recommendation_service import (
    compute_recommendation,
    get_recommendations,
)

router = APIRouter()


@router.post("/{user_id}", tags=["Recommendations"])
def calculate_recommendation(user_id: int, db: Session = Depends(database.get_db)):
    try:
        compute_recommendation(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Could not compute. Exception: {e}"
        )
    return {"status_code": 200, "detail": "Recommendation compute completed"}


@router.get("/{user_id}", tags=["Recommendations"])
def fetch_recommendations(user_id: int, db: Session = Depends(database.get_db)):
    try:
        user_preferences = fetch_user_preferences(db, user_id)
        recommended_books = get_recommendations(db, user_preferences)
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Could not find recommendation. Exception: {e}"
        )
    return recommended_books
