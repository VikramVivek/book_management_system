import pytest

def test_generate_book_summary(client, create_test_book, admin_token):
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(f"/summarization/books/{book_id}/summary", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) > 0  # Ensure that the summary is generated

def test_generate_review_summary(client, create_test_review, admin_token):
    book_id = create_test_review["book_id"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(f"/summarization/books/{book_id}/reviews/summary", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) > 0  # Ensure that the summary is generated
    assert "reviews" in data
    assert len(data["reviews"]) > 0  # Ensure that reviews were used

def test_generate_book_summary_book_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(f"/summarization/books/999/summary", headers=headers)  # Non-existent book_id
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

def test_generate_review_summary_no_reviews(client, create_test_book, admin_token):
    book_id = create_test_book["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(f"/summarization/books/{book_id}/reviews/summary", headers=headers)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this book"
