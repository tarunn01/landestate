import io
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from app.tasks import notify_image_uploaded, validate_image, notify_broker


# ============================================================================
# notify_image_uploaded
# ============================================================================


@pytest.mark.unit
def test_notify_image_uploaded_returns_none():
    result = notify_image_uploaded("prop-1", "https://fake.com/img.jpg")
    assert result is None


# ============================================================================
# validate_image
# ============================================================================


@pytest.mark.unit
def test_validate_image_valid_jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()

    with patch("app.tasks.S3Service") as MockS3:
        MockS3.return_value.download_image.return_value = jpeg_bytes
        result = validate_image("prop-1", "properties/test/img.jpg")

    assert result == {"Valid": True, "property_id": "prop-1"}


@pytest.mark.unit
def test_validate_image_valid_png():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buf, format="PNG")
    png_bytes = buf.getvalue()

    with patch("app.tasks.S3Service") as MockS3:
        MockS3.return_value.download_image.return_value = png_bytes
        result = validate_image("prop-1", "properties/test/img.png")

    assert result == {"Valid": True, "property_id": "prop-1"}


@pytest.mark.unit
def test_validate_image_invalid_format_raises():
    with patch("app.tasks.S3Service") as MockS3, patch("app.tasks.Image") as MockImage:
        MockS3.return_value.download_image.return_value = b"fake bytes"
        mock_img = MagicMock()
        mock_img.format = "GIF"
        MockImage.open.return_value = mock_img

        with pytest.raises(ValueError):
            validate_image("prop-1", "properties/test/img.gif")


@pytest.mark.unit
def test_validate_image_too_large_raises():
    with patch("app.tasks.S3Service") as MockS3, patch("app.tasks.Image") as MockImage:
        MockS3.return_value.download_image.return_value = b"x" * (6 * 1024 * 1024)
        mock_img = MagicMock()
        mock_img.format = "JPEG"
        MockImage.open.return_value = mock_img

        with pytest.raises(ValueError):
            validate_image("prop-1", "properties/test/big.jpg")


# ============================================================================
# notify_broker
# ============================================================================


@pytest.mark.unit
def test_notify_broker_success():
    with patch("app.tasks.SessionLocal") as MockSession:
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_prop = MagicMock()
        mock_prop.broker.email = "broker@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_prop

        result = notify_broker(
            {"Valid": True, "property_id": "prop-1"},
            "https://fake.com/img.jpg",
        )

    assert result == {"notified": True}
    mock_db.close.assert_called_once()
