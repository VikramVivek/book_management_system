from unittest.mock import AsyncMock, patch


@patch("app.routers.summarization.generate_summary_for_content", new_callable=AsyncMock)
def test_generate_book_summary(
    mock_generate_summary, client, create_test_book, admin_token
):
    # Set up the mock to return a specific value
    mock_generate_summary.return_value = "This is a mocked summary."
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(f"/summarization/books/{book_id}/summary", headers=headers)

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
    mock_generate_review_summary.return_value = "This is a mocked review summary."
    book_id = create_test_review["book_id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        f"/summarization/books/{book_id}/reviews/summary", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert (
        data["summary"] == "This is a mocked review summary."
    )  # Ensure that the summary is generated
    assert "reviews" in data
    assert len(data["reviews"]) > 0  # Ensure that reviews were used


def test_generate_book_summary_book_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        "/summarization/books/999/summary", headers=headers
    )  # Non-existent book_id

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_generate_review_summary_no_reviews(client, create_test_book, admin_token):
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        f"/summarization/books/{book_id}/reviews/summary", headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this book"
