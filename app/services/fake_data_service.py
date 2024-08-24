import random

from faker import Faker
from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.database import get_db
from app.models import Book, Review, User, UserPreferences

fake = Faker()

# Example positive, negative, and neutral review templates
positive_templates = [
    "I absolutely loved this book! The characters were so well-developed, ",
    "and the plot was gripping from start to finish. An amazing read! ",
    "I couldn't put it down. Highly recommend to anyone who loves {genre}.",
    "This book exceeded my expectations! A must-read for fans of {author}.",
]

negative_templates = [
    "I was disappointed with this book. The plot was slow and the characters",
    " were flat. Not worth the time. I expected more from {author}.",
    "This book just didn't do it for me. The story felt disjointed and the ",
    "ending was unsatisfying.",
]

neutral_templates = [
    "This book was okay. It had some good moments but overall it was just ",
    "average. An okay read. Nothing too special but not bad either.",
    "The book was fine, but it didn't leave a lasting impression on me.",
]

genres = [
    "Fiction",
    "Science Fiction",
    "Non-Fiction",
    "Fantasy",
    "Romance",
    "Thriller",
    "Mystery",
    "Historical",
    "Biography",
    "Self-Help",
]


def generate_realistic_content():
    return fake.text(max_nb_chars=5000)


def generate_review(genre, author, sentiment):
    if sentiment == "positive":
        template = random.choice(positive_templates)
    elif sentiment == "negative":
        template = random.choice(negative_templates)
    else:
        template = random.choice(neutral_templates)

    return template.format(genre=genre, author=author)


def generate_fake_data(
    user_count: int = 10,
    book_count: int = 20,
    review_count: int = 100,
    positive_review_percent: int = 50,
    negative_review_percent: int = 25,
    neutral_review_percent: int = 25,
    db: Session = Depends(get_db),
):
    # Generate fake users and their preferences
    users = []
    for _ in range(user_count):
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            hashed_password=get_password_hash("password"),
        )
        db.add(user)
        db.commit()

        # Assign user preferences
        preferences = UserPreferences(
            user_id=user.id,
            preferred_genres=", ".join(random.sample(genres, k=2)),
            preferred_authors=", ".join(
                [f"{fake.first_name()} {fake.last_name()}" for _ in range(2)]
            ),
        )
        db.add(preferences)
        db.commit()

        users.append(user)

    # Generate fake books
    books = []
    for _ in range(book_count):
        genre = random.choice(genres)
        author = f"{fake.first_name()} {fake.last_name()}"
        book = Book(
            title=fake.sentence(nb_words=4),
            author=author,
            genre=genre,
            year_of_publication=random.randint(1950, 2024),
            content=generate_realistic_content(),
            summary=fake.paragraph(nb_sentences=2),
        )
        db.add(book)
        books.append(book)
    db.commit()

    # Generate fake reviews
    for _ in range(review_count):
        sentiment = random.choices(
            ["positive", "negative", "neutral"],
            weights=[
                positive_review_percent,
                negative_review_percent,
                neutral_review_percent,
            ],
            k=1,
        )[0]

        book = random.choice(books)
        review_text = generate_review(book.genre, book.author, sentiment)
        review = Review(
            book_id=book.id,
            user_id=random.choice(users).id,
            review_text=review_text,
            rating=(
                5 if sentiment == "positive" else (3 if sentiment == "neutral" else 1)
            ),
        )
        db.add(review)
    db.commit()
