import pytest

def test_get_profile(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"

def test_update_profile(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put("/users/me", headers=headers, json={
        "email": "updateduser@example.com",
        "username": "updatedusername",
        "password": "newpassword"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "updateduser@example.com"

def test_set_preferences(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/users/preferences/", json={
        "preferred_genres": "Fiction,Science Fiction",
        "preferred_authors": "Author 1,Author 2"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_genres"] == "Fiction,Science Fiction"
    assert data["preferred_authors"] == "Author 1,Author 2"

@pytest.fixture(scope="function")
def setup_preferences(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/users/preferences/", json={
        "preferred_genres": "Fiction,Science Fiction",
        "preferred_authors": "Author 1,Author 2"
    }, headers=headers)
    return response

def test_get_preferences(client, user_token, setup_preferences):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/preferences/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_genres"] == "Fiction,Science Fiction"
    assert data["preferred_authors"] == "Author 1,Author 2"

def test_get_preferences_not_set(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/preferences/", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User preferences not found"