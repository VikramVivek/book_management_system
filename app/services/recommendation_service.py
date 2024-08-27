import json
import logging
import os
import pickle
from datetime import datetime

import boto3
from fastapi import HTTPException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sqlalchemy.orm import Session

from app.models import Book, Recommendation, User, UserPreferences

from ..config import REDIS_CACHE_TTL
from .mock_redis_service import redis_client

# Set up logger
logger = logging.getLogger("app.recommendation_service")

CACHE_TTL = REDIS_CACHE_TTL  # Cache Time-To-Live in seconds

# Use an environment variable to switch between local and AWS SageMaker
USE_SAGEMAKER = os.getenv("USE_SAGEMAKER", "false").lower() == "true"

if USE_SAGEMAKER:
    sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="your-region")
    sagemaker_endpoint_name = "your-sagemaker-endpoint-name"
    logger.info("Using SageMaker for recommendations")
else:
    logger.info("Using local model for recommendations")


def train_recommendation_model(db: Session):
    """
    Train the recommendation model using TF-IDF and Nearest Neighbors.

    Args:
        db (Session): Database session.

    Returns:
        dict: A message indicating the model was trained successfully.
    """
    logger.info("Starting model training")
    books = db.query(Book).all()
    if not books:
        logger.error("No books found for training the model")
        raise ValueError("No books found for training the model")

    # Prepare the data
    book_data = [
        f"{book.genre} {book.author} {book.summary} {book.content}" for book in books
    ]

    # Train a simple model using TF-IDF and Nearest Neighbors
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(book_data)

    model = NearestNeighbors(n_neighbors=10, algorithm="auto").fit(X)

    # Save the model and vectorizer to a file
    with open("recommendation_model.pkl", "wb") as model_file:
        pickle.dump((model, vectorizer, [book.id for book in books]), model_file)
    logger.info("Model trained and saved successfully")

    return {"detail": "Model trained successfully"}


def get_recommendations(db: Session, user_preferences: UserPreferences):
    """
    Get book recommendations for a user based on their preferences.

    Args:
        db (Session): Database session.
        user_preferences (UserPreferences): User preferences for genres and authors.

    Returns:
        list: List of recommended books.
    """
    logger.info(f"Fetching recommendations for user_id {user_preferences.user_id}")
    cache_key = f"recommendations:{user_preferences.user_id}"

    # Check if recommendations are already in the cache
    cached_recommendations = redis_client.get(cache_key)
    if cached_recommendations:
        logger.debug("Recommendations fetched from cache")
        return json.loads(cached_recommendations)

    if USE_SAGEMAKER:
        recommended_books = get_recommendations_from_sagemaker(user_preferences)
    else:
        recommended_books = get_recommendations_locally(db, user_preferences)

    # Cache the recommendations with an expiration time
    redis_client.setex(
        cache_key, CACHE_TTL, json.dumps([book.id for book in recommended_books])
    )
    logger.debug("Recommendations cached")

    return recommended_books


def get_recommendations_locally(db: Session, user_preferences: UserPreferences):
    """
    Get recommendations locally using the trained model.

    Args:
        db (Session): Database session.
        user_preferences (UserPreferences): User preferences for genres and authors.

    Returns:
        list: List of recommended books.
    """
    logger.info("Fetching recommendations locally")
    with open("recommendation_model.pkl", "rb") as model_file:
        model, vectorizer, book_ids = pickle.load(model_file)

    # Prepare the user's preference data for recommendation
    preference_text = (
        f"{user_preferences.preferred_genres} {user_preferences.preferred_authors}"
    )
    X_user = vectorizer.transform([preference_text])

    # Get recommendations
    distances, indices = model.kneighbors(X_user)

    # Retrieve recommended books from the database
    recommended_books = [db.query(Book).get(book_ids[i]) for i in indices[0]]
    logger.debug(f"Recommendations generated for user_id {user_preferences.user_id}")

    return recommended_books


def get_recommendations_from_sagemaker(user_preferences: UserPreferences):
    """
    Get recommendations using AWS SageMaker.

    Args:
        user_preferences (UserPreferences): User preferences for genres and authors.

    Returns:
        list: List of recommended books.
    """
    logger.info("Fetching recommendations from SageMaker")
    payload = json.dumps(
        {
            "preferred_genres": user_preferences.preferred_genres,
            "preferred_authors": user_preferences.preferred_authors,
        }
    )

    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=sagemaker_endpoint_name,
        ContentType="application/json",
        Body=payload,
    )

    recommendations = json.loads(response["Body"].read().decode())
    logger.debug(
        "Received recommendations from SageMaker for ",
        f"user_id {user_preferences.user_id}",
    )

    return recommendations


def precompute_recommendations_for_all_users(db: Session):
    """
    Precompute recommendations for all users and store them in the database.

    Args:
        db (Session): Database session.
    """
    logger.info("Precomputing recommendations for all users")
    users = db.query(User).all()
    for user in users:
        user_preferences = (
            db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        )

        if not user_preferences:
            logger.debug(f"No preferences found for user_id {user.id}")
            continue

        # Get personalized recommendations based on the model
        recommended_books_ids = get_recommendations(db, user_preferences)
        recommended_books_serialized = json.dumps(recommended_books_ids)

        existing_recommendation = (
            db.query(Recommendation).filter(Recommendation.user_id == user.id).first()
        )

        if existing_recommendation:
            existing_recommendation.recommended_books = recommended_books_serialized
            existing_recommendation.updated_at = datetime.utcnow()
        else:
            new_recommendation = Recommendation(
                user_id=user.id,
                recommended_books=recommended_books_serialized,
            )
            db.add(new_recommendation)

        db.commit()
    logger.info("Precomputed recommendations for all users")


def compute_recommendation(db: Session, user_id: int):
    """
    Compute recommendations for a specific user.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user.

    Raises:
        HTTPException: If the user's preferences are not set.

    Returns:
        None
    """
    logger.info(f"Computing recommendation for user_id {user_id}")
    user_preferences = (
        db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    )

    if not user_preferences:
        logger.error(f"User preferences not found for user_id {user_id}")
        raise HTTPException(status_code=404, detail="User preference not set")

    # Get personalized recommendations based on the model
    recommended_books_ids = get_recommendations(db, user_preferences)
    recommended_books_serialized = json.dumps(recommended_books_ids)

    existing_recommendation = (
        db.query(Recommendation).filter(Recommendation.user_id == user_id).first()
    )

    if existing_recommendation:
        existing_recommendation.recommended_books = recommended_books_serialized
        existing_recommendation.updated_at = datetime.utcnow()
    else:
        new_recommendation = Recommendation(
            user_id=user_id,
            recommended_books=recommended_books_serialized,
        )
        db.add(new_recommendation)

    db.commit()
    logger.info(f"Recommendation computed and stored for user_id {user_id}")
