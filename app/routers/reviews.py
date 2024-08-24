import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas

# Setup logger
logger = logging.getLogger("app.reviews")

router = APIRouter()


@router.post("/", response_model=schemas.Review, tags=["Review Management"])
def create_review(
    review: schemas.ReviewCreate,
    book_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """
    Create a new review for a book.

    Args:
        review (schemas.ReviewCreate): The review data to be created.
        book_id (int): The ID of the book being reviewed.
        db (Session): Database session dependency.
        current_user (schemas.User): The current logged-in user.

    Returns:
        schemas.Review: The created review.

    Raises:
        HTTPException: If there is an error during the creation process.
    """
    logger.info(f"Creating review for book ID: {book_id} by user ID: {current_user.id}")
    try:
        db_review = models.Review(
            **review.dict(), book_id=book_id, user_id=current_user.id
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        logger.info(f"Review created successfully for book ID: {book_id}")
    except Exception as e:
        logger.error(f"Failed to create review for book ID: {book_id}. Exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to create review")
    return db_review


@router.get("/{review_id}", response_model=schemas.Review, tags=["Review Management"])
def read_review(
    review_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """
    Retrieve a review by its ID.

    Args:
        review_id (int): The ID of the review to be retrieved.
        db (Session): Database session dependency.
        current_user (schemas.User): The current logged-in user.

    Returns:
        schemas.Review: The retrieved review.

    Raises:
        HTTPException: If the review is not found.
    """
    logger.info(f"Fetching review ID: {review_id}")
    result = db.execute(select(models.Review).filter(models.Review.id == review_id))
    db_review = result.scalar_one_or_none()
    if db_review is None:
        logger.warning(f"Review ID: {review_id} not found")
        raise HTTPException(status_code=404, detail="Review not found")
    logger.info(f"Review ID: {review_id} fetched successfully")
    return db_review


@router.put("/{review_id}", response_model=schemas.Review, tags=["Review Management"])
def update_review(
    review_id: int,
    review_update: schemas.ReviewCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """
    Update an existing review by its ID.

    Args:
        review_id (int): The ID of the review to be updated.
        review_update (schemas.ReviewCreate): The updated review data.
        db (Session): Database session dependency.
        current_user (schemas.User): The current logged-in user.

    Returns:
        schemas.Review: The updated review.

    Raises:
        HTTPException: If the review is not found or if the user is not authorized
                       to update the review.
    """
    logger.info(f"Updating review ID: {review_id} by user ID: {current_user.id}")
    db_review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id, models.Review.user_id == current_user.id)
        .first()
    )
    if not db_review:
        logger.warning(f"Review ID: {review_id} not found or unauthorized access")
        raise HTTPException(status_code=404, detail="Review not found")

    db_review.review_text = review_update.review_text
    db_review.rating = review_update.rating
    db.commit()
    db.refresh(db_review)
    logger.info(f"Review ID: {review_id} updated successfully")
    return db_review


@router.delete("/{review_id}", tags=["Review Management"])
def delete_review(
    review_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """
    Delete a review by its ID.

    Args:
        review_id (int): The ID of the review to be deleted.
        db (Session): Database session dependency.
        current_user (schemas.User): The current logged-in user.

    Returns:
        dict: A confirmation message that the review was deleted.

    Raises:
        HTTPException: If the review is not found or if the user is not authorized
                       to delete the review.
    """
    logger.info(f"Deleting review ID: {review_id} by user ID: {current_user.id}")
    db_review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id, models.Review.user_id == current_user.id)
        .first()
    )
    if not db_review:
        logger.warning(f"Review ID: {review_id} not found or unauthorized access")
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(db_review)
    db.commit()
    logger.info(f"Review ID: {review_id} deleted successfully")
    return {"detail": "Review deleted"}
