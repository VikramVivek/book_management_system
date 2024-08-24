import logging

# Set up a logger for the test
logger = logging.getLogger(__name__)


def test_admin_get_all_users(client, admin_token):
    """
    Test that an admin can retrieve a list of all users.
    """
    logger.info("Testing admin's ability to get all users.")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users", headers=headers)

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_update_user(client, admin_token):
    """
    Test that an admin can update a user's details.
    """
    logger.info("Testing admin's ability to update a user.")

    # First, create a user to update
    response = client.post(
        "/auth/register",
        json={
            "email": "updatableuser@example.com",
            "username": "updatableuser",
            "password": "updatepassword",
        },
    )
    user_id = response.json()["id"]
    logger.debug(f"Created user ID: {user_id}")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"/admin/users/{user_id}",
        headers=headers,
        json={
            "email": "newemail@example.com",
            "username": "newusername",
            "password": "newpassword",
            "role": "user",
        },
    )

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


def test_admin_delete_user(client, admin_token):
    """
    Test that an admin can delete a user.
    """
    logger.info("Testing admin's ability to delete a user.")

    # First, create a user to delete
    response = client.post(
        "/auth/register",
        json={
            "email": "deletableuser@example.com",
            "username": "deletableuser",
            "password": "deletepassword",
        },
    )
    user_id = response.json()["id"]
    logger.debug(f"Created user ID: {user_id}")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/admin/users/{user_id}", headers=headers)

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"


def test_admin_update_review(client, admin_token, create_test_review):
    """
    Test that an admin can update a review.
    """
    logger.info("Testing admin's ability to update a review.")

    headers = {"Authorization": f"Bearer {admin_token}"}
    review_id = create_test_review["id"]
    response = client.put(
        f"/admin/reviews/{review_id}",
        json={"review_text": "Admin has updated this review.", "rating": 2},
        headers=headers,
    )

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "Admin has updated this review."
    assert data["rating"] == 2


def test_admin_delete_review(client, admin_token, create_test_review):
    """
    Test that an admin can delete a review.
    """
    logger.info("Testing admin's ability to delete a review.")

    headers = {"Authorization": f"Bearer {admin_token}"}
    review_id = create_test_review["id"]
    response = client.delete(f"/admin/reviews/{review_id}", headers=headers)

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response data: {response.json()}")

    assert response.status_code == 200
    assert response.json()["detail"] == "Review deleted"

    # Verify that the review was actually deleted
    response = client.get(f"/reviews/{review_id}", headers=headers)

    logger.debug(f"Verification response status code: {response.status_code}")

    assert response.status_code == 404
