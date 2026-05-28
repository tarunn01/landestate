import pytest
from fastapi import status
from pydantic import ValidationError
from unittest.mock import patch


@pytest.mark.unit
def test_list_properties_empty(client):
    response = client.get("/api/v1/properties")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.unit
def test_create_property(client, valid_token, test_location_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "title": "sample_title",
        "description": "sample description",
        "location_id": test_location_in_db.location_id,
        "price": 120000,
        "city": "hyderabad",
        "address": "local address ",
        "contact_phone": "7893450879",
    }
    response = client.post(
        "api/v1/properties",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "sample_title"


@pytest.mark.unit
def test_create_property_no_auth(client, test_location_in_db):
    payload = {
        "title": "sample_title",
        "description": "sample description",
        "location_id": test_location_in_db.location_id,
        "price": 120000,
        "city": "hyderabad",
        "address": "local address ",
        "contact_phone": "7893450879",
    }
    response = client.post(
        "/api/v1/properties",
        json=payload,
    )
    assert response.status_code == 401


@pytest.mark.unit
def test_get_property(test_property_in_db, client):
    response = client.get(
        f"/api/v1/properties/{test_property_in_db.id}",
    )
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == test_property_in_db.id


@pytest.mark.unit
def test_get_property_not_found(client):
    response = client.get("/api/v1/properties/nonexistent-id-xyz")
    assert response.status_code == 404


@pytest.mark.unit
def test_list_properties_with_data(client, test_property_in_db):
    response = client.get("/api/v1/properties")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == test_property_in_db.id


@pytest.mark.unit
def test_list_properties_pagination(client, test_property_in_db):
    response = client.get("/api/v1/properties?skip=0&limit=1")
    data = response.json()
    assert response.status_code == 200
    assert data["limit"] == 1
    assert data["skip"] == 0


@pytest.mark.unit
def test_list_properties_cache_hit(client, mock_dependencies):
    import json

    cached = json.dumps({"total": 99, "skip": 0, "limit": 10, "items": []})
    mock_dependencies.get.return_value = cached
    response = client.get("/api/v1/properties")
    assert response.status_code == 200
    assert response.json()["total"] == 99


@pytest.mark.unit
def test_update_property_success(client, valid_token, test_property_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Updated Title Here", "price": 999999}
    response = client.put(
        f"/api/v1/properties/{test_property_in_db.id}",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title Here"
    assert response.json()["price"] == 999999


@pytest.mark.unit
def test_update_property_forbidden(client, admin_token, test_property_in_db):
    """Admin user cannot update a property owned by someone else."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"/api/v1/properties/{test_property_in_db.id}",
        headers=headers,
        json={"title": "Unauthorized Update"},
    )
    assert response.status_code == 403


@pytest.mark.unit
def test_update_property_no_auth(client, test_property_in_db):
    response = client.put(
        f"/api/v1/properties/{test_property_in_db.id}",
        json={"title": "No Auth Update"},
    )
    assert response.status_code == 401


@pytest.mark.unit
def test_update_property_not_found(client, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.put(
        "/api/v1/properties/nonexistent-id-xyz",
        headers=headers,
        json={"title": "Ghost Property"},
    )
    assert response.status_code == 404


@pytest.mark.unit
def test_delete_property_success(client, valid_token, test_property_in_db):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.delete(
        f"/api/v1/properties/{test_property_in_db.id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_property_in_db.id

    # Confirm it's gone
    get_response = client.get(f"/api/v1/properties/{test_property_in_db.id}")
    assert get_response.status_code == 404


@pytest.mark.unit
def test_delete_property_forbidden(client, admin_token, test_property_in_db):
    """Admin user cannot delete a property owned by someone else."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(
        f"/api/v1/properties/{test_property_in_db.id}",
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.unit
def test_delete_property_no_auth(client, test_property_in_db):
    response = client.delete(f"/api/v1/properties/{test_property_in_db.id}")
    assert response.status_code == 401


@pytest.mark.unit
def test_upload_image_property_not_found(client, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.post(
        "/api/v1/properties/nonexistent-id-xyz/images",
        headers=headers,
        files={"file": ("test.jpg", b"fake bytes", "image/jpeg")},
    )
    assert response.status_code == 404


@pytest.mark.unit
def test_upload_image_forbidden(client, admin_token, test_property_in_db):
    """A user who is not the broker cannot upload images."""
    with (
        patch("app.services.s3.S3Service.upload_image") as mock_upload,
        patch("app.api.v1.properties.chain") as mock_chain,
    ):
        mock_upload.return_value = ("key", "https://fake.com/img.jpg")
        mock_chain.return_value.apply_async.return_value = None
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            f"/api/v1/properties/{test_property_in_db.id}/images",
            headers=headers,
            files={"file": ("test.jpg", b"fake bytes", "image/jpeg")},
        )
    assert response.status_code == 403


@pytest.mark.unit
def test_delete_image_property_not_found(client, valid_token, test_image_in_db):
    with patch("app.services.s3.S3Service.delete_image"):
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.delete(
            f"/api/v1/properties/nonexistent-id-xyz/images/{test_image_in_db.id}",
            headers=headers,
        )
    assert response.status_code == 404


@pytest.mark.unit
def test_delete_image_not_found(client, valid_token, test_property_in_db):
    with patch("app.services.s3.S3Service.delete_image"):
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.delete(
            f"/api/v1/properties/{test_property_in_db.id}/images/nonexistent-image-id",
            headers=headers,
        )
    assert response.status_code == 404
