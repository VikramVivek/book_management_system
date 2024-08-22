from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..auth import get_current_active_user, get_password_hash
from ..services.fake_data_service import generate_fake_data
from ..services.recommendation_service import train_recommendation_model
from ..services.create_admin_service import create_admin

router = APIRouter()

@router.get("/users", response_model=list[schemas.User], tags=["User Management", "Admin"])
def get_all_users(current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User, tags=["User Management", "Admin"])
def admin_update_user(user_id: int, user_update: schemas.UserCreate, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.email = user_update.email
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    return schemas.User.from_orm(user)

@router.delete("/users/{user_id}", tags=["User Management", "Admin"])
def admin_delete_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

# Admin-specific endpoints for managing reviews
@router.put("/reviews/{review_id}", response_model=schemas.Review, tags=["Review Management", "Admin"])
def admin_update_review(review_id: int, review_update: schemas.ReviewCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    db_review.review_text = review_update.review_text
    db_review.rating = review_update.rating
    db.commit()
    db.refresh(db_review)
    return db_review

@router.delete("/reviews/{review_id}", tags=["Review Management", "Admin"])
def admin_delete_review(review_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(db_review)
    db.commit()
    return {"detail": "Review deleted"}


@router.post("/users/{user_id}/preferences/", response_model=schemas.UserPreferences, tags=["Recommendations", "User Management", "Admin"])
def set_user_preferences(user_id: int, preferences: schemas.UserPreferencesCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_preferences = db.query(models.UserPreferences).filter(models.UserPreferences.user_id == user_id).first()
    
    if db_preferences:
        db_preferences.preferred_genres = preferences.preferred_genres
        db_preferences.preferred_authors = preferences.preferred_authors
    else:
        db_preferences = models.UserPreferences(**preferences.dict(), user_id=user_id)
        db.add(db_preferences)
    
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

@router.get("/users/{user_id}/preferences/", response_model=schemas.UserPreferences, tags=["Recommendations", "User Management", "Admin"])
def get_user_preferences(user_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_preferences = db.query(models.UserPreferences).filter(models.UserPreferences.user_id == user_id).first()

    if not db_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return db_preferences

@router.post("/fake-data", tags=["Admin","Setup Test Env"])
def fake_data(
    user_count: int = 10, 
    book_count: int = 20, 
    review_count: int = 100, 
    db: Session = Depends(database.get_db)
):
    try:
        generate_fake_data(user_count, book_count, review_count, db)
    except:
        raise HTTPException(status_code=503, detail="Fake Data Not Generated")

    return {"detail": "Fake data generated successfully"}

@router.post("/create-admin", tags=["Admin","Setup Test Env"])
def create_admin_for_test(
    email: str = 'admin@example.com', 
    username: str = 'admin', 
    password: str = 'adminpassword', 
    db: Session = Depends(database.get_db)
):
    try:
        create_admin(email, username, password, db)
    except:
        raise HTTPException(status_code=503, detail="Admin Not Created")
    return {"detail": "Admin created successfully"}

@router.post("/train-recommendation-model", tags=["Admin"])
def train_model_endpoint(db: Session = Depends(database.get_db)):
    result = train_recommendation_model(db)
    return result
