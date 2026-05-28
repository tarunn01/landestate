import pytest
from fastapi import status
from pydantic import ValidationError


@pytest.mark.unit
def test_create_review_success(client, valid_token, test_property_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "feedback": "good area for living ",
        "rating": 3,
        "property_id": test_property_in_db.id,
    }
    response = client.post("/api/v1/reviews", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json()["rating"] == 3


@pytest.mark.unit
def test_create_review_fail(client, test_property_in_db):

    payload = {
        "feedback": "good area for living ",
        "rating": 3,
        "property_id": test_property_in_db.id,
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 401


@pytest.mark.unit
def test_create_review_fail_rating(client, test_property_in_db, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "feedback": "good area for living ",
        "rating": 6,
        "property_id": test_property_in_db.id,
    }
    response = client.post("/api/v1/reviews", headers=headers, json=payload)
    assert response.status_code == 422


@pytest.mark.unit
def test_update_review_success(client, valid_token, test_property_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    # payload = {"rating": 5, "feedback": "very good","property_id": test_property_in_db.id}

    create_res = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={"rating": 5, "feedback": "very good", "property_id": test_property_in_db.id},
    )
    review_id = create_res.json()["review_id"]
    response = client.put(
        f"/api/v1/reviews/{review_id}",
        headers=headers,
        json={
            "feedback": "updated feedback",
            "rating": 5,
        },
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5


@pytest.mark.unit
def test_update_review_success(client, admin_token, valid_token, test_property_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    # payload = {"rating": 5, "feedback": "very good","property_id": test_property_in_db.id}

    create_res = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={"rating": 5, "feedback": "very good", "property_id": test_property_in_db.id},
    )
    review_id = create_res.json()["review_id"]
    headers2 = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"/api/v1/reviews/{review_id}",
        headers=headers2,
        json={
            "feedback": "updated feedback",
            "rating": 5,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "not authorized"
