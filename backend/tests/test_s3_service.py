import io
from unittest.mock import patch, MagicMock
from app.services import s3
from app.services.s3 import S3Service
from app.core.config import settings


def test_upload_image(client, valid_token, test_property_in_db):
    with (
        patch("app.services.s3.S3Service.upload_image") as mock_upload,
        patch("app.api.v1.properties.chain") as mock_chain,
    ):
        mock_upload.return_value = (
            "properties/test/image.jpg",
            "https://fake-s3-url.com/image.jpg",
        )
        mock_chain.return_value.apply_async.return_value = None
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.post(
            f"/api/v1/properties/{test_property_in_db.id}/images",
            headers=headers,
            files={"file": ("test.jpg", b"fake images bytes", "images/jpeg")},
        )
        assert response.status_code == 201


def test_delete_image(client, valid_token, test_property_in_db, test_image_in_db):
    with patch("app.services.s3.S3Service.delete_image") as mock_delete:
        mock_delete.return_value = None

        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.delete(
            f"/api/v1/properties/{test_property_in_db.id}/images/{test_image_in_db.id}",
            headers=headers,
        )
        assert response.status_code == 200


# ============================================================================
# S3Service unit tests (boto3 mocked — no real AWS calls)
# ============================================================================


def test_s3_upload_image_unit():
    with patch("app.services.s3.boto3") as mock_boto:
        mock_client = MagicMock()
        mock_boto.client.return_value = mock_client

        s3_svc = S3Service()
        fake_file = io.BytesIO(b"fake image data")
        key, url = s3_svc.upload_image(fake_file, "prop-123", "photo.jpg")

        assert key.startswith("properties/prop-123/")
        assert key.endswith("photo.jpg")
        assert settings.S3_BUCKET_NAME in url
        assert "prop-123" in key
        mock_client.upload_fileobj.assert_called_once()


def test_s3_delete_image_unit():
    with patch("app.services.s3.boto3") as mock_boto:
        mock_client = MagicMock()
        mock_boto.client.return_value = mock_client

        s3_svc = S3Service()
        s3_svc.delete_image("properties/test/fake-key.jpg")

        mock_client.delete_object.assert_called_once_with(
            Bucket=settings.S3_BUCKET_NAME,
            Key="properties/test/fake-key.jpg",
        )


def test_s3_download_image_unit():
    with patch("app.services.s3.boto3") as mock_boto:
        mock_client = MagicMock()
        mock_boto.client.return_value = mock_client

        fake_bytes = b"raw image bytes here"
        mock_body = MagicMock()
        mock_body.read.return_value = fake_bytes
        mock_client.get_object.return_value = {"Body": mock_body}

        s3_svc = S3Service()
        result = s3_svc.download_image("properties/test/fake-key.jpg")

        assert result == fake_bytes
        mock_client.get_object.assert_called_once_with(
            Bucket=settings.S3_BUCKET_NAME,
            Key="properties/test/fake-key.jpg",
        )
