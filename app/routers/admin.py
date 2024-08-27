import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..auth import get_current_active_user, get_password_hash
from ..services.create_admin_service import create_admin
from ..services.fake_data_service import generate_fake_data
from ..services.recommendation_service import train_recommendation_model

# Setup logger
logger = logging.getLogger("app.admin")

router = APIRouter()


@router.get(
    "/users", response_model=list[schemas.User], tags=["User Management", "Admin"]
)
def get_all_users(
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db),
):
    """
    Retrieve all users from the database.

    Args:
        current_user (schemas.User): The current active user.
        db (Session): The database session.

    Returns:
        list[schemas.User]: A list of all users.
    """
    logger.info("Fetching all users.")
    users = db.query(models.User).all()
    return users


@router.put(
    "/users/{user_id}", response_model=schemas.User, tags=["User Management", "Admin"]
)
def admin_update_user(
    user_id: int,
    user_update: schemas.UserCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db),
):
    """
    Update a user's details.

    Args:
        user_id (int): The ID of the user to update.
        user_update (schemas.UserCreate): The updated user details.
        current_user (schemas.User): The current active user.
        db (Session): The database session.

    Returns:
        schemas.User: The updated user.
    """
    logger.info(f"Updating user with ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")

    user.email = user_update.email
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)
    logger.info(f"User with ID {user_id} updated successfully.")
    return schemas.User.from_orm(user)


@router.delete("/users/{user_id}", tags=["User Management", "Admin"])
def admin_delete_user(
    user_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db),
):
    """
    Delete a user from the database.

    Args:
        user_id (int): The ID of the user to delete.
        current_user (schemas.User): The current active user.
        db (Session): The database session.

    Returns:
        dict: A confirmation message.
    """
    logger.info(f"Deleting user with ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    logger.info(f"User with ID {user_id} deleted successfully.")
    return {"detail": "User deleted"}


@router.put(
    "/reviews/{review_id}",
    response_model=schemas.Review,
    tags=["Review Management", "Admin"],
)
def admin_update_review(
    review_id: int,
    review_update: schemas.ReviewCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Update a review's details.

    Args:
        review_id (int): The ID of the review to update.
        review_update (schemas.ReviewCreate): The updated review details.
        db (Session): The database session.
        current_user (schemas.User): The current active user.

    Returns:
        schemas.Review: The updated review.
    """
    logger.info(f"Updating review with ID: {review_id}")
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        logger.warning(f"Review with ID {review_id} not found.")
        raise HTTPException(status_code=404, detail="Review not found")
    db_review.review_text = review_update.review_text
    db_review.rating = review_update.rating
    db.commit()
    db.refresh(db_review)
    logger.info(f"Review with ID {review_id} updated successfully.")
    return db_review


@router.delete("/reviews/{review_id}", tags=["Review Management", "Admin"])
def admin_delete_review(
    review_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Delete a review from the database.

    Args:
        review_id (int): The ID of the review to delete.
        db (Session): The database session.
        current_user (schemas.User): The current active user.

    Returns:
        dict: A confirmation message.
    """
    logger.info(f"Deleting review with ID: {review_id}")
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        logger.warning(f"Review with ID {review_id} not found.")
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(db_review)
    db.commit()
    logger.info(f"Review with ID {review_id} deleted successfully.")
    return {"detail": "Review deleted"}


@router.post(
    "/users/{user_id}/preferences/",
    response_model=schemas.UserPreferences,
    tags=["Recommendations", "User Management", "Admin"],
)
def set_user_preferences(
    user_id: int,
    preferences: schemas.UserPreferencesCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Set or update user preferences.

    Args:
        user_id (int): The ID of the user.
        preferences (schemas.UserPreferencesCreate): The user's preferences.
        db (Session): The database session.
        current_user (schemas.User): The current active user.

    Returns:
        schemas.UserPreferences: The updated or created user preferences.
    """
    logger.info(f"Setting preferences for user ID: {user_id}")
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == user_id)
        .first()
    )

    if db_preferences:
        db_preferences.preferred_genres = preferences.preferred_genres
        db_preferences.preferred_authors = preferences.preferred_authors
    else:
        db_preferences = models.UserPreferences(**preferences.dict(), user_id=user_id)
        db.add(db_preferences)

    db.commit()
    db.refresh(db_preferences)
    logger.info(f"Preferences for user ID {user_id} set successfully.")
    return db_preferences


@router.get(
    "/users/{user_id}/preferences/",
    response_model=schemas.UserPreferences,
    tags=["Recommendations", "User Management", "Admin"],
)
def get_user_preferences(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retrieve user preferences.

    Args:
        user_id (int): The ID of the user.
        db (Session): The database session.
        current_user (schemas.User): The current active user.

    Returns:
        schemas.UserPreferences: The user's preferences.
    """
    logger.info(f"Fetching preferences for user ID: {user_id}")
    db_preferences = (
        db.query(models.UserPreferences)
        .filter(models.UserPreferences.user_id == user_id)
        .first()
    )

    if not db_preferences:
        logger.warning(f"Preferences for user ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User preferences not found")

    return db_preferences


@router.post("/fake-data", tags=["Admin", "Setup Test Env"])
def fake_data(
    user_count: int = 10,
    book_count: int = 20,
    review_count: int = 100,
    positive_review_percent: int = 50,
    negative_review_percent: int = 25,
    neutral_review_percent: int = 25,
    db: Session = Depends(database.get_db),
):
    """
    Generate fake data for testing purposes.

    Args:
        user_count (int): The number of users to generate.
        book_count (int): The number of books to generate.
        review_count (int): The number of reviews to generate.
        positive_review_percent (int): The percentage of positive reviews.
        negative_review_percent (int): The percentage of negative reviews.
        neutral_review_percent (int): The percentage of neutral reviews.
        db (Session): The database session.

    Returns:
        dict: A confirmation message.
    """
    logger.info("Generating fake data")
    try:
        generate_fake_data(
            user_count,
            book_count,
            review_count,
            positive_review_percent,
            negative_review_percent,
            neutral_review_percent,
            db,
        )
    except Exception as e:
        logger.error("Failed to generate fake data: %s", e)
        raise HTTPException(
            status_code=503, detail=f"Fake Data Not Generated. Exception: {e}"
        )

    logger.info("Fake data generated successfully")
    return {"detail": "Fake data generated successfully"}


@router.post("/create-admin", tags=["Admin", "Setup Test Env"])
def create_admin_for_test(
    email: str = "admin@example.com",
    username: str = "admin",
    password: str = "adminpassword",
    db: Session = Depends(database.get_db),
):
    """
    Create an admin user for testing purposes.

    Args:
        email (str): The email of the admin user.
        username (str): The username of the admin user.
        password (str): The password of the admin user.
        db (Session): The database session.

    Returns:
        dict: A confirmation message.
    """
    logger.info("Creating admin user")
    try:
        create_admin(email, username, password, db)
    except Exception as e:
        logger.error("Failed to create admin user: %s", e)
        raise HTTPException(
            status_code=503, detail=f"Admin Not Created. Exception: {e}"
        )
    logger.info("Admin user created successfully")
    return {"detail": "Admin created successfully"}


@router.post("/train-recommendation-model", tags=["Admin"])
def train_model_endpoint(db: Session = Depends(database.get_db)):
    """
    Train the recommendation model.

    Args:
        db (Session): The database session.

    Returns:
        dict: A confirmation message.
    """
    logger.info("Training recommendation model")
    result = train_recommendation_model(db)
    logger.info("Recommendation model trained successfully")
    return result


@router.post("/reset-database", tags=["Admin", "Setup Test Env"])
def reset_db_for_test(
    db: Session = Depends(database.get_db),
):
    """
    Reset the database for testing purposes.

    Args:
        db (Session): The database session.

    Returns:
        dict: A confirmation message.
    """
    logger.info("Resetting database")
    try:
        database.reset_db()
    except Exception as e:
        logger.error("Database reset failed: %s", e)
        raise HTTPException(
            status_code=503, detail=f"Database reset failed. Exception: {e}"
        )
    logger.info("Database reset successfully")
    return {"detail": "Database reset successful"}
