import logging

# Set up a logger for the test
logger = logging.getLogger(__name__)


def test_registration(client):
    """
    Test that a new user can register successfully.
    """
    logger.info("Testing user registration.")

    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword",
        },
    )

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"


def test_login(client, user_token):
    """
    Test that a registered user can log in and receive an access token.
    """
    logger.info("Testing user login.")

    response = client.post(
        "/auth/token",
        data={"username": "testuser@example.com", "password": "testpassword"},
    )

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert "access_token" in response.json()
