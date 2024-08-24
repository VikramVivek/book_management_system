import logging
from unittest.mock import AsyncMock, patch

# Set up a logger for the test
logger = logging.getLogger(__name__)


@patch("app.routers.summarization.generate_summary_for_content", new_callable=AsyncMock)
def test_generate_book_summary(
    mock_generate_summary, client, create_test_book, admin_token
):
    """
    Test that a book summary is successfully generated using the mocked
    summarization service.
    """
    logger.info("Testing generate book summary endpoint.")
    # Set up the mock to return a specific value
    mock_generate_summary.return_value = "This is a mocked summary."
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(f"/summarization/books/{book_id}/summary", headers=headers)

    logger.debug(f"Generate book summary response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert (
        data["summary"] == "This is a mocked summary."
    )  # Ensure that the summary is generated


@patch("app.routers.summarization.generate_summary_for_reviews")
def test_generate_review_summary(
    mock_generate_review_summary, client, create_test_review, admin_token
):
    """
    Test that a review summary is successfully generated using the mocked
    summarization service.
    """
    logger.info("Testing generate review summary endpoint.")
    mock_generate_review_summary.return_value = "This is a mocked review summary."
    book_id = create_test_review["book_id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        f"/summarization/books/{book_id}/reviews/summary", headers=headers
    )

    logger.debug(f"Generate review summary response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert (
        data["summary"] == "This is a mocked review summary."
    )  # Ensure that the summary is generated
    assert "reviews" in data
    assert len(data["reviews"]) > 0  # Ensure that reviews were used


def test_generate_book_summary_book_not_found(client, admin_token):
    """
    Test that a 404 error is returned when attempting to generate a summary
    for a non-existent book.
    """
    logger.info("Testing generate book summary endpoint for non-existent book.")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        "/summarization/books/999/summary", headers=headers
    )  # Non-existent book_id

    logger.debug(f"Book not found response: {response.json()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_generate_review_summary_no_reviews(client, create_test_book, admin_token):
    """
    Test that a 404 error is returned when attempting to generate a summary
    for a book with no reviews.
    """
    logger.info("Testing generate review summary endpoint for book with no reviews.")
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        f"/summarization/books/{book_id}/reviews/summary", headers=headers
    )

    logger.debug(f"No reviews found response: {response.json()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this book"
