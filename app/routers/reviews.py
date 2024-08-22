from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from .. import schemas, models, database, auth

router = APIRouter()

# Get a review
@router.get("/{review_id}", response_model=schemas.Review, tags=["Review Management"])
def read_review(review_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    result = db.execute(select(models.Review).filter(models.Review.id == review_id))
    db_review = result.scalar_one_or_none()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

# Add a review
@router.post("/", response_model=schemas.Review, tags=["Review Management"])
def create_review(review: schemas.ReviewCreate, book_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_review = models.Review(**review.dict(), book_id=book_id, user_id=current_user.id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

# Edit a review
@router.put("/{review_id}", response_model=schemas.Review, tags=["Review Management"])
def update_review(review_id: int, review_update: schemas.ReviewCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id, models.Review.user_id == current_user.id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    db_review.review_text = review_update.review_text
    db_review.rating = review_update.rating
    db.commit()
    db.refresh(db_review)
    return db_review

# Delete a review
@router.delete("/{review_id}", tags=["Review Management"])
def delete_review(review_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id, models.Review.user_id == current_user.id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(db_review)
    db.commit()
    return {"detail": "Review deleted"}
