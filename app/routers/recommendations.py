from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
import json
from ..services.recommendation_service import precompute_recommendations_for_all_users, get_recommendations, compute_recommendation

router = APIRouter()

@router.post("/{user_id}", tags=["Recommendations"])
def calculate_recommendation(user_id: int, db: Session = Depends(database.get_db)):
    try:
        compute_recommendation(db, user_id)
    except:
        raise HTTPException(status_code=404, detail="Could not compute")
    return ({"status_code":200, "detail":"Recommendation compute completed"})

@router.get("/{user_id}", tags=["Recommendations"])
def fetch_recommendations(user_id: int, db: Session = Depends(database.get_db)):
    try:
        recommended_books = get_recommendations(db, user_id)
    except:
        raise HTTPException(status_code=404, detail="Could not find recommendation")
    return recommended_books