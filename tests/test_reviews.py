import logging

# Set up a logger for the test
logger = logging.getLogger(__name__)


def test_read_review(client, user_token, create_test_review):
    """
    Test that the read review endpoint returns the correct review data.
    """
    logger.info("Testing read review endpoint.")
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]
    review_text = create_test_review["review_text"]

    response = client.get(f"/reviews/{review_id}", headers=headers)

    logger.debug(f"Read review response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["review_text"] == review_text


def test_create_review(client, user_token, create_test_book):
    """
    Test that a review can be successfully created for a book.
    """
    logger.info("Testing create review endpoint.")
    headers = {"Authorization": f"Bearer {user_token}"}
    book_id = create_test_book["id"]

    response = client.post(
        "/reviews",
        json={"review_text": "This is a test review for creation.", "rating": 4},
        params={"book_id": book_id},
        headers=headers,
    )

    logger.debug(f"Create review response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "This is a test review for creation."
    assert data["rating"] == 4
    assert data["book_id"] == book_id


def test_update_review(client, user_token, create_test_review):
    """
    Test that an existing review can be successfully updated.
    """
    logger.info("Testing update review endpoint.")
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]

    response = client.put(
        f"/reviews/{review_id}",
        json={"review_text": "This review has been updated.", "rating": 3},
        headers=headers,
    )

    logger.debug(f"Update review response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "This review has been updated."
    assert data["rating"] == 3


def test_delete_review(client, user_token, create_test_review):
    """
    Test that a review can be successfully deleted.
    """
    logger.info("Testing delete review endpoint.")
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]

    response = client.delete(f"/reviews/{review_id}", headers=headers)

    logger.debug(f"Delete review response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Review deleted"

    # Verify that the review was actually deleted
    response = client.get(f"/reviews/{review_id}", headers=headers)
    logger.debug(f"Verify deletion response: {response.status_code}")
    assert response.status_code == 404
