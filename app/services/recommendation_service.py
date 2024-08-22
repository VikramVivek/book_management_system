import json
import pickle
from datetime import datetime

from fastapi import HTTPException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sqlalchemy.orm import Session

from app.models import Book, Recommendation, User, UserPreferences


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


def precompute_recommendations_for_all_users(db: Session):
    users = db.query(User).all()
    for user in users:
        user_preferences = (
            db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        )

        if not user_preferences:
            continue

        # Get personalized recommendations based on the model
        recommended_books = get_recommendations(db, user_preferences)
        recommended_books_ids = [book.id for book in recommended_books]
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
    recommended_books = get_recommendations(db, user_preferences)
    recommended_books_ids = [book.id for book in recommended_books]
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
