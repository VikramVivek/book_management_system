import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Review
from app.services.summarization_service import (
    generate_summary_for_content,
    generate_summary_for_reviews,
)

# Setup logger
logger = logging.getLogger("app.summarization")

router = APIRouter()


@router.post("/books/{book_id}/summary", tags=["Book Summarization"])
async def generate_book_summary(book_id: int, db: Session = Depends(get_db)):
    """
    Generate a summary for a specific book based on its content.

    Args:
        book_id (int): The ID of the book for which the summary is to be generated.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing the generated summary.

    Raises:
        HTTPException: If the book is not found.
    """
    logger.info(f"Generating summary for book ID: {book_id}")
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        logger.warning(f"Book ID: {book_id} not found")
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        summary = await generate_summary_for_content(book.content)
        book.summary = summary
        db.commit()
        logger.info(f"Summary generated successfully for book ID: {book_id}")
    except Exception as e:
        logger.error(
            f"Failed to generate summary for book ID: {book_id}. Exception: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to generate summary")

    return {"summary": summary}


@router.post("/books/{book_id}/reviews/summary", tags=["Book Summarization"])
def generate_review_summary(book_id: int, db: Session = Depends(get_db)):
    """
    Generate a summary for the reviews of a specific book.

    Args:
        book_id (int): The ID of the book for which the review summary is to be
                       generated.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing the review texts and the generated summary.

    Raises:
        HTTPException: If no reviews are found for the specified book.
    """
    logger.info(f"Generating review summary for book ID: {book_id}")
    reviews = db.query(Review).filter(Review.book_id == book_id).all()
    if not reviews:
        logger.warning(f"No reviews found for book ID: {book_id}")
        raise HTTPException(status_code=404, detail="No reviews found for this book")

    try:
        review_texts = [
            f"User Review: {review.review_text} || User Rating: {review.rating}"
            for review in reviews
        ]
        summary = generate_summary_for_reviews(review_texts)
        logger.info(f"Review summary generated successfully for book ID: {book_id}")
    except Exception as e:
        logger.error(
            f"Failed to generate review summary for book ID: {book_id}. Exception: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to generate review summary")

    return {"reviews": review_texts, "summary": summary}
