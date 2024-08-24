import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import auth, models
from app.database import Base, get_db
from app.main import create_app

# Configuration for the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Fixture to set up and tear down the test database.
    Ensures a clean state before each test and cleans up after the test is run.
    """
    Base.metadata.drop_all(bind=engine)  # Drop all tables before creating new ones
    Base.metadata.create_all(bind=engine)  # Create tables
    yield
    Base.metadata.drop_all(bind=engine)  # Drop all tables after test execution


def override_get_db():
    """
    Dependency override for getting a database session.
    This override provides a session from the test database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def app():
    """
    Fixture to create the FastAPI app with dependency overrides.
    This allows tests to use the test database instead of the production database.
    """
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    yield app


@pytest.fixture(scope="function")
def client(app):
    """
    Fixture to create a test client for sending requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture to create a database session for use in tests.
    The session is automatically closed after each test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def admin_token(client, db_session):
    """
    Fixture to create an admin user and return a valid JWT token for the admin.
    The admin user is created only if it does not already exist.
    """
    existing_admin = (
        db_session.query(models.User).filter_by(email="admin@example.com").first()
    )
    if not existing_admin:
        db_session.add(
            models.User(
                email="admin@example.com",
                username="admin",
                hashed_password=auth.get_password_hash("adminpassword"),
                role="admin",
            )
        )
        db_session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def user_token(client, db_session):
    """
    Fixture to create a regular user and return a valid JWT token for the user.
    The user is created only if it does not already exist.
    """
    existing_user = (
        db_session.query(models.User).filter_by(email="testuser@example.com").first()
    )
    if not existing_user:
        db_session.add(
            models.User(
                email="testuser@example.com",
                username="testuser",
                hashed_password=auth.get_password_hash("testpassword"),
                role="user",
            )
        )
        db_session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "testuser@example.com", "password": "testpassword"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def create_test_book(client, admin_token):
    """
    Fixture to create a test book using the admin credentials.
    Returns the JSON response of the created book.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/books",
        json={
            "title": "Test Book for Reviews",
            "author": "Test Author",
            "genre": "Fiction",
            "year_of_publication": 2024,
            "content": "Content of the book used for review tests.",
        },
        headers=headers,
    )
    return response.json()


@pytest.fixture(scope="function")
def create_test_review(client, user_token, create_test_book):
    """
    Fixture to create a test review for the test book.
    Returns the JSON response of the created review.
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    book_id = create_test_book["id"]
    response = client.post(
        "/reviews",
        json={"review_text": "This is a test review.", "rating": 5},
        params={"book_id": book_id},
        headers=headers,
    )
    return response.json()


@pytest.fixture(scope="function")
def set_user_preferences(client, user_token):
    """
    Fixture to set user preferences for the logged-in user.
    Returns the JSON response of the set preferences.
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/users/preferences/",
        json={
            "preferred_genres": "Fiction,Science Fiction",
            "preferred_authors": "Test Author",
        },
        headers=headers,
    )
    return response.json()
