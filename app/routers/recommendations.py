import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.user_service import fetch_user_preferences

from .. import database
from ..services.recommendation_service import (
    compute_recommendation,
    get_recommendations,
)

# Setup logger
logger = logging.getLogger("app.recommendations")

router = APIRouter()


@router.post("/{user_id}", tags=["Recommendations"])
def calculate_recommendation(user_id: int, db: Session = Depends(database.get_db)):
    """
    Calculate and store book recommendations for a given user based on preferences.

    Args:
        user_id (int): The ID of the user for whom to calculate recommendations.
        db (Session): Database session dependency.

    Returns:
        dict: A confirmation message that the recommendation computation was completed.

    Raises:
        HTTPException: If the recommendation computation fails.
    """
    logger.info(f"Calculating recommendations for user ID: {user_id}")
    try:
        compute_recommendation(db, user_id)
        logger.info(f"Recommendations successfully computed for user ID: {user_id}")
    except Exception as e:
        logger.error(
            f"Failed to compute recommendations for user ID: {user_id}. Exception: {e}"
        )
        raise HTTPException(
            status_code=404, detail=f"Could not compute. Exception: {e}"
        )
    return {"status_code": 200, "detail": "Recommendation compute completed"}


@router.get("/{user_id}", tags=["Recommendations"])
def fetch_recommendations(user_id: int, db: Session = Depends(database.get_db)):
    """
    Fetch personalized book recommendations for a given user based on their preferences.

    Args:
        user_id (int): The ID of the user to fetch recommendations for.
        db (Session): Database session dependency.

    Returns:
        list[schemas.Book]: A list of recommended books.

    Raises:
        HTTPException: If no recommendations could be found for the user.
    """
    logger.info(f"Fetching recommendations for user ID: {user_id}")
    try:
        user_preferences = fetch_user_preferences(db, user_id)
        recommended_books = get_recommendations(db, user_preferences)
        logger.info(f"Recommendations fetched successfully for user ID: {user_id}")
    except Exception as e:
        logger.error(
            f"Failed to fetch recommendations for user ID: {user_id}. Exception: {e}"
        )
        raise HTTPException(
            status_code=404, detail=f"Could not find recommendation. Exception: {e}"
        )
    return recommended_books
