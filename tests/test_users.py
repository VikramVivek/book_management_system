import logging

import pytest

# Set up a logger for the test
logger = logging.getLogger(__name__)


def test_get_profile(client, user_token):
    """
    Test retrieving the current user's profile.
    """
    logger.info("Testing user profile retrieval.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/me", headers=headers)

    logger.debug(f"User profile response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


def test_update_profile(client, user_token):
    """
    Test updating the current user's profile.
    """
    logger.info("Testing user profile update.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put(
        "/users/me",
        headers=headers,
        json={
            "email": "updateduser@example.com",
            "username": "updatedusername",
            "password": "newpassword",
        },
    )

    logger.debug(f"User profile update response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["email"] == "updateduser@example.com"


def test_set_preferences(client, user_token):
    """
    Test setting user preferences.
    """
    logger.info("Testing setting user preferences.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/users/preferences/",
        json={
            "preferred_genres": "Fiction,Science Fiction",
            "preferred_authors": "Author 1,Author 2",
        },
        headers=headers,
    )

    logger.debug(f"Set preferences response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_genres"] == "Fiction,Science Fiction"
    assert data["preferred_authors"] == "Author 1,Author 2"


@pytest.fixture(scope="function")
def setup_preferences(client, user_token):
    """
    Fixture to set up user preferences for testing.
    """
    logger.info("Setting up user preferences fixture.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/users/preferences/",
        json={
            "preferred_genres": "Fiction,Science Fiction",
            "preferred_authors": "Author 1,Author 2",
        },
        headers=headers,
    )
    logger.debug(f"Setup preferences fixture response: {response.json()}")
    return response


def test_get_preferences(client, user_token, setup_preferences):
    """
    Test retrieving user preferences after they have been set.
    """
    logger.info("Testing user preferences retrieval.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/preferences/", headers=headers)

    logger.debug(f"Get preferences response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_genres"] == "Fiction,Science Fiction"
    assert data["preferred_authors"] == "Author 1,Author 2"


def test_get_preferences_not_set(client, user_token):
    """
    Test retrieving user preferences when they have not been set.
    """
    logger.info("Testing user preferences retrieval when not set.")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/preferences/", headers=headers)

    logger.debug(f"Get preferences not set response: {response.json()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User preferences not found"
