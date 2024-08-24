import json
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

CACHE_TTL = REDIS_CACHE_TTL  # Cache Time-To-Live in seconds

# Use an environment variable to switch between local and AWS SageMaker
USE_SAGEMAKER = os.getenv("USE_SAGEMAKER", "false").lower() == "true"

if USE_SAGEMAKER:
    sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="your-region")
    sagemaker_endpoint_name = "your-sagemaker-endpoint-name"


def train_recommendation_model(db: Session):
    books = db.query(Book).all()
    if not books:
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

    return {"detail": "Model trained successfully"}


def get_recommendations(db: Session, user_preferences: UserPreferences):
    # Generate a unique cache key based on user preferences
    cache_key = f"recommendations:{user_preferences.user_id}"

    # Check if recommendations are already in the cache
    cached_recommendations = redis_client.get(cache_key)
    if cached_recommendations:
        return json.loads(cached_recommendations)

    if USE_SAGEMAKER:
        recommended_books = get_recommendations_from_sagemaker(user_preferences)
    else:
        recommended_books = get_recommendations_locally(db, user_preferences)

    # Cache the recommendations with an expiration time
    redis_client.setex(
        cache_key, CACHE_TTL, json.dumps([book.id for book in recommended_books])
    )

    return recommended_books


def get_recommendations_locally(db: Session, user_preferences: UserPreferences):
    # Load the trained model and vectorizer
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

    return recommended_books


def get_recommendations_from_sagemaker(user_preferences: UserPreferences):
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

    return recommendations


def precompute_recommendations_for_all_users(db: Session):
    users = db.query(User).all()
    for user in users:
        user_preferences = (
            db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        )

        if not user_preferences:
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


def compute_recommendation(db: Session, user_id: int):
    user_preferences = (
        db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    )

    if not user_preferences:
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
