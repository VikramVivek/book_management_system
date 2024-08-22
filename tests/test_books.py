import pytest


@pytest.fixture(scope="function")
def create_test_book(client, admin_token):
    # Create a book that other tests can rely on
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/books",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Fiction",
            "year_of_publication": 2024,
            "content": "This is a test book content.",
        },
        headers=headers,
    )
    return response.json()


def test_create_book(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/books",
        json={
            "title": "Another Test Book",
            "author": "Another Author",
            "genre": "Fiction",
            "year_of_publication": 2025,
            "content": "This is another test book content.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Another Test Book"
    assert data["author"] == "Another Author"


def test_get_books(client, user_token, create_test_book):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/books", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Ensure there's at least one book in the list


def test_get_book_by_id(client, user_token, create_test_book):
    headers = {"Authorization": f"Bearer {user_token}"}
    book_id = create_test_book["id"]
    response = client.get(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == create_test_book["title"]
    assert data["author"] == create_test_book["author"]


def test_update_book(client, admin_token, create_test_book):
    headers = {"Authorization": f"Bearer {admin_token}"}
    book_id = create_test_book["id"]
    response = client.put(
        f"/books/{book_id}",
        json={
            "title": "Updated Book Title",
            "author": "Updated Author",
            "genre": "Updated Genre",
            "year_of_publication": 2025,
            "content": "This is the updated content.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Book Title"
    assert data["author"] == "Updated Author"


def test_delete_book(client, admin_token, create_test_book):
    headers = {"Authorization": f"Bearer {admin_token}"}
    book_id = create_test_book["id"]
    response = client.delete(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == create_test_book["title"]

    # Verify the book was actually deleted
    response = client.get(f"/books/{book_id}", headers=headers)
    assert response.status_code == 404
