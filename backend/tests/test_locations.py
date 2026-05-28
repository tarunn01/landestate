import pytest
from fastapi import status
from pydantic import ValidationError


@pytest.mark.unit
def test_list_locations_success(client):
    response = client.get(
        "/api/v1/locations",
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_create_location_success(client, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "name": "hyd",
        "latitude": 41.40338,
        "longitude": 2.17403,
        "state": "telangana",
        "country": "india",
        "description": "NAAA",
    }
    response = client.post("/api/v1/locations", headers=headers, json=payload)
    assert response.status_code == 200


@pytest.mark.unit
def test_create_location_no_auth(
    client,
):

    payload = {
        "name": "hyd",
        "latitude": 41.40338,
        "longitude": 2.17403,
        "state": "telangana",
        "country": "india",
        "description": "NAAA",
    }
    response = client.post("/api/v1/locations", json=payload)
    assert response.status_code == 401


@pytest.mark.unit
def test_get_location_detail(client, valid_token, test_location_in_db):

    response = client.get(
        f"/api/v1/locations/{test_location_in_db.location_id}",
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_get_location_not_found(client):
    response = client.get(
        f"/api/v1/locations/fake-id-76587",
    )
    assert response.status_code == 404


@pytest.mark.unit
def test_update_location_success(client, test_location_in_db, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "name": "sample loc",
        "country": "europe",
        "state": "west coast",
        "longitude": 41.40338,
        "latitude": 41.49338,
        "description": "nice location",
    }
    response = client.put(
        f"/api/v1/locations/{test_location_in_db.location_id}", headers=headers, json=payload
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_update_location_forbidden(client, test_location_in_db, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "name": "sample loc",
        "country": "indiana",
    }
    response = client.put(
        f"/api/v1/locations/{test_location_in_db.location_id}", headers=headers, json=payload
    )
    assert response.status_code == 403


@pytest.mark.unit
def test_delete_location_success(client, test_location_in_db, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/api/v1/locations/{test_location_in_db.location_id}", headers=headers
    )
    assert response.status_code == 200
