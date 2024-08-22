import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import create_app
from app import models, auth

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # Ensure a clean test database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup database after each test
    Base.metadata.drop_all(bind=engine)

# Override the dependency for `get_db`
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def app():
    # Set up the app and dependency overrides
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    yield app

@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def admin_token(client, db_session):
    # Check if the admin already exists
    existing_admin = db_session.query(models.User).filter_by(email="admin@example.com").first()
    # If the admin does not exist, create a new one
    if not existing_admin:
        db_session.add(models.User(
            email="admin@example.com",
            username="admin",
            hashed_password=auth.get_password_hash("adminpassword"),
            role="admin"
        ))
        db_session.commit()
    
    # Now get the token for the user (whether newly created or existing)
    response = client.post("/auth/token", data={
        "username": "admin@example.com",
        "password": "adminpassword"
    })
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def user_token(client, db_session):
    # Check if the user already exists
    existing_user = db_session.query(models.User).filter_by(email="testuser@example.com").first()
    # If the user does not exist, create a new one
    if not existing_user:
        db_session.add(models.User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=auth.get_password_hash("testpassword"),
            role="user"
        ))
        db_session.commit()

    # Now get the token for the user (whether newly created or existing)
    response = client.post("/auth/token", data={
        "username": "testuser@example.com",
        "password": "testpassword"
    })
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def create_test_book(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/books", json={
        "title": "Test Book for Reviews",
        "author": "Test Author",
        "genre": "Fiction",
        "year_of_publication": 2024,
        "content": "Content of the book used for review tests."
    }, headers=headers)
    return response.json()

@pytest.fixture(scope="function")
def create_test_review(client, user_token, create_test_book):
    headers = {"Authorization": f"Bearer {user_token}"}
    book_id = create_test_book["id"]
    response = client.post("/reviews", json={
        "review_text": "This is a test review.",
        "rating": 5
    }, params={"book_id": book_id}, headers=headers)
    return response.json()

@pytest.fixture(scope="function")
def set_user_preferences(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/users/preferences/", json={
        "preferred_genres": "Fiction,Science Fiction",
        "preferred_authors": "Test Author"
    }, headers=headers)
    return response.json()