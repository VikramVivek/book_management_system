from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # Add role field
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    recommendations = relationship("Recommendation", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    genre = Column(String, index=True)
    year_of_publication = Column(Integer)
    content = Column(Text)
    summary = Column(Text, default="Summary is being generated")  # New field to store the book summary

    reviews = relationship("Review", back_populates="book")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_text = Column(String)
    rating = Column(Integer)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preferred_genres = Column(String, nullable=False)
    preferred_authors = Column(String, nullable=False)

    user = relationship("User", back_populates="preferences")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_books = Column(Text, nullable=False)  # Store book IDs as JSON or comma-separated list
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="recommendations")
