from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Book, Review
from app.services.summarization_service import generate_summary_for_content, generate_summary_for_reviews

router = APIRouter()

@router.post("/books/{book_id}/summary", tags=["Book Summarization"])
def generate_book_summary(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    summary = generate_summary_for_content(book.content)
    book.summary = summary
    db.commit()
    
    return {"summary": summary}

@router.post("/books/{book_id}/reviews/summary", tags=["Book Summarization"])
def generate_review_summary(book_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.book_id == book_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this book")

    review_texts = [f"User Review: {review.review_text} || User Rating: {review.rating}" for review in reviews]
    summary = generate_summary_for_reviews(review_texts)
    
    return {"reviews":review_texts,"summary": summary}
