import json
from unittest.mock import patch

import pytest


# Mock Redis connection in the tests
@pytest.fixture(scope="function", autouse=True)
def mock_redis():
    with patch(
        "app.services.recommendation_service.redis_client", autospec=True
    ) as mock_redis_client:
        # Mock the 'get' method to return a JSON-encoded string
        # representing the recommended books
        mock_recommended_books = [
            {
                "title": "Mock Book",
                "author": "Test Author",
                "genre": "Fiction",
                "year_of_publication": 2024,
            }
        ]
        mock_redis_client.get.return_value = json.dumps(mock_recommended_books).encode(
            "utf-8"
        )
        yield mock_redis_client


# Test for calculating recommendations
def test_calculate_recommendation(
    client, user_token, db_session, set_user_preferences, mock_redis
):
    headers = {"Authorization": f"Bearer {user_token}"}

    with patch(
        "app.services.recommendation_service.compute_recommendation"
    ) as mock_compute:
        mock_compute.return_value = None  # Mock the function to not actually compute

        response = client.post("/recommendations/1", headers=headers)

        assert response.status_code == 200
        assert response.json() == {
            "status_code": 200,
            "detail": "Recommendation compute completed",
        }


# Test for fetching recommendations
def test_fetch_recommendations(
    client, user_token, db_session, set_user_preferences, mock_redis
):
    headers = {"Authorization": f"Bearer {user_token}"}

    mock_recommended_books = [
        {
            "title": "Mock Book",
            "author": "Test Author",
            "genre": "Fiction",
            "year_of_publication": 2024,
        }
    ]

    with patch(
        "app.services.recommendation_service.get_recommendations"
    ) as mock_get_recommendations:
        mock_get_recommendations.return_value = mock_recommended_books

        response = client.get("/recommendations/1", headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["title"] == "Mock Book"
