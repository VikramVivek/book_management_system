from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Book, Review
from app.auth import get_password_hash
from faker import Faker
import random

fake = Faker()

def generate_fake_data(
    user_count: int = 10, 
    book_count: int = 20, 
    review_count: int = 100, 
    db: Session = Depends(get_db)
):
    # Generate fake users
    users = []
    for _ in range(user_count):
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            hashed_password=get_password_hash("password"),
        )
        db.add(user)
        users.append(user)
    db.commit()

    # Generate fake books
    books = []
    for _ in range(book_count):
        book = Book(
            title=fake.sentence(nb_words=4),
            author=f"{fake.first_name()} {fake.last_name()}",
            genre=random.choice(["Fiction", "Science Fiction", "Non-Fiction", "Fantasy"]),
            year_of_publication=random.randint(1950, 2024),
            content=fake.paragraph(nb_sentences=10),
            summary=fake.paragraph(nb_sentences=2)
        )
        db.add(book)
        books.append(book)
    db.commit()

    # Generate fake reviews
    for _ in range(review_count):
        review = Review(
            book_id=random.choice(books).id,
            user_id=random.choice(users).id,
            review_text=fake.paragraph(nb_sentences=3),
            rating=random.randint(1, 5)
        )
        db.add(review)
    db.commit()

