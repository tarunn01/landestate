from PIL import Image
import io


from app.celery_app import celery_app
from app.services.s3 import S3Service
from app.core.database import SessionLocal
from app.models.properties import Property as PropertyModel


@celery_app.task
def notify_image_uploaded(property_id: str, image_url: str):
    print(f"new image uploaded for property {property_id}:{image_url}")


@celery_app.task
def validate_image(property_id: str, s3_key: str):
    image_bytes = S3Service().download_image(s3_key)
    img = Image.open(io.BytesIO(image_bytes))
    if img.format not in ("JPEG", "PNG"):
        raise ValueError
    if len(image_bytes) > 5 * 1024 * 1024:
        raise ValueError
    return {"Valid": True, "property_id": property_id}


@celery_app.task
def notify_broker(validation_result: dict, image_url: str):
    property_id = validation_result["property_id"]
    db = SessionLocal()
    prop = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    broker_email = prop.broker.email
    print(f"Notifying broker {broker_email}: new image uploaded {image_url}")
    db.close()
    return {"notified": True}
