from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator, ConfigDict


class ReviewCreateRequest(BaseModel):
    feedback: str = Field(..., description="short suggestion/complaint you faced")
    rating: int = Field(..., ge=1, le=5, description=" rating between 1 - 5")
    property_id: str = Field(..., description="property id ")


class ReviewResponse(BaseModel):
    feedback: str = Field(..., description="short suggestion/complaint you faced")
    rating: int = Field(..., ge=1, le=5, description=" rating between 1 - 5")
    reviewer_id: str = Field(..., description="your user id here")
    created_at: datetime = Field(..., description=" review created timestamp ")
    property_id: str = Field(..., description="property id ")
    review_id: str = Field(..., description="id of the review")

    model_config = ConfigDict(from_attributes=True)


class ReviewUpdateRequest(BaseModel):
    feedback: Optional[str] = Field(None, description="short suggestion/complaint you faced")
    rating: Optional[int] = Field(None, ge=1, le=5, description="rating between 1 - 5")
