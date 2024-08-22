def test_admin_get_all_users(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_update_user(client, admin_token):
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
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


def test_admin_delete_user(client, admin_token):
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

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/admin/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"


def test_admin_update_review(client, admin_token, create_test_review):
    headers = {"Authorization": f"Bearer {admin_token}"}
    review_id = create_test_review["id"]
    response = client.put(
        f"/admin/reviews/{review_id}",
        json={"review_text": "Admin has updated this review.", "rating": 2},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "Admin has updated this review."
    assert data["rating"] == 2


def test_admin_delete_review(client, admin_token, create_test_review):
    headers = {"Authorization": f"Bearer {admin_token}"}
    review_id = create_test_review["id"]
    response = client.delete(f"/admin/reviews/{review_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Review deleted"

    # Verify that the review was actually deleted
    response = client.get(f"/reviews/{review_id}", headers=headers)
    assert response.status_code == 404
