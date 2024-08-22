
def test_registration(client):
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"

def test_login(client, user_token):
    response = client.post("/auth/token", data={
        "username": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()