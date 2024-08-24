import datetime
import logging

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

# Setup logger
logger = logging.getLogger("app.models")

Base = declarative_base()


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The primary key for the user.
        email (str): The unique email address of the user.
        username (str): The unique username of the user.
        hashed_password (str): The hashed password for the user.
        role (str): The role of the user, e.g., 'user' or 'admin'.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    recommendations = relationship("Recommendation", back_populates="user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"User {self.username} created")


class Book(Base):
    """
    Represents a book in the system.

    Attributes:
        id (int): The primary key for the book.
        title (str): The title of the book.
        author (str): The author of the book.
        genre (str): The genre of the book.
        year_of_publication (int): The year the book was published.
        content (str): The content of the book.
        summary (str): The summary of the book.
    """

    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    genre = Column(String, index=True)
    year_of_publication = Column(Integer)
    content = Column(Text)
    summary = Column(Text, default="Summary is being generated")

    reviews = relationship("Review", back_populates="book")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Book '{self.title}' by {self.author} added to the database")


class Review(Base):
    """
    Represents a review in the system.

    Attributes:
        id (int): The primary key for the review.
        book_id (int): The foreign key linking to the book being reviewed.
        user_id (int): The foreign key linking to the user who wrote the review.
        review_text (str): The text content of the review.
        rating (int): The rating given in the review.
    """

    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_text = Column(String)
    rating = Column(Integer)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Review by user {self.user_id} for book {self.book_id} added")


class UserPreferences(Base):
    """
    Represents user preferences in the system.

    Attributes:
        id (int): The primary key for the user preferences.
        user_id (int): The foreign key linking to the user.
        preferred_genres (str): The user's preferred genres.
        preferred_authors (str): The user's preferred authors.
    """

    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preferred_genres = Column(String, nullable=False)
    preferred_authors = Column(String, nullable=False)

    user = relationship("User", back_populates="preferences")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Preferences for user {self.user_id} set")


class Recommendation(Base):
    """
    Represents book recommendations for a user.

    Attributes:
        id (int): The primary key for the recommendation.
        user_id (int): The foreign key linking to the user.
        recommended_books (str): The book IDs recommended for the user.
        created_at (datetime): The timestamp when the recommendation was created.
        updated_at (datetime): The timestamp when the recommendation was last updated.
    """

    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_books = Column(
        Text, nullable=False
    )  # Store book IDs as JSON or comma-separated list
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user = relationship("User", back_populates="recommendations")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Recommendations generated for user {self.user_id}")
