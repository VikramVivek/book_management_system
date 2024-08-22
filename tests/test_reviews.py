def test_read_review(client, user_token, create_test_review):
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]
    review_text = create_test_review["review_text"]
    response = client.get(f"/reviews/{review_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["review_text"] == review_text


def test_create_review(client, user_token, create_test_book):
    headers = {"Authorization": f"Bearer {user_token}"}
    book_id = create_test_book["id"]
    response = client.post(
        "/reviews",
        json={"review_text": "This is a test review for creation.", "rating": 4},
        params={"book_id": book_id},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "This is a test review for creation."
    assert data["rating"] == 4
    assert data["book_id"] == book_id


def test_update_review(client, user_token, create_test_review):
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]
    response = client.put(
        f"/reviews/{review_id}",
        json={"review_text": "This review has been updated.", "rating": 3},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "This review has been updated."
    assert data["rating"] == 3


def test_delete_review(client, user_token, create_test_review):
    headers = {"Authorization": f"Bearer {user_token}"}
    review_id = create_test_review["id"]
    response = client.delete(f"/reviews/{review_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Review deleted"

    # Verify that the review was actually deleted
    response = client.get(f"/reviews/{review_id}", headers=headers)
    assert response.status_code == 404
