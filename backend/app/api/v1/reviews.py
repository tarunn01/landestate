from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.reviews import Review as ReviewModel
from app.models.properties import Property as propertyModel
from app.schemas.reviews import ReviewCreateRequest, ReviewResponse, ReviewUpdateRequest


router = APIRouter(tags=["Reviews"])


class ReviewResource:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def list_review(
        self,
        property_id: str,
        skip: int = 0,
        limit: int = 10,
    ) -> dict:
        reviews = (
            self.db.query(ReviewModel)
            .filter(ReviewModel.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        total = self.db.query(ReviewModel).filter(ReviewModel.property_id == property_id).count()
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [ReviewResponse.model_validate(review) for review in reviews],
        }

    async def get_review(self, review_id: str):
        review = self.db.query(ReviewModel).filter(ReviewModel.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review not found")
        return ReviewResponse.model_validate(review)

    async def create_review(
        self, review_in: ReviewCreateRequest, current_user: dict
    ) -> ReviewResponse:
        # create a review here
        new_review = ReviewModel(
            reviewer_id=current_user.id,
            feedback=review_in.feedback,
            rating=review_in.rating,
            property_id=review_in.property_id,
        )
        self.db.add(new_review)
        self.db.commit()
        self.db.refresh(new_review)
        return ReviewResponse.model_validate(new_review)

    async def update_review(
        self, current_user: dict, review_id: str, review_in: ReviewUpdateRequest
    ):
        review = self.db.query(ReviewModel).filter(ReviewModel.review_id == review_id).first()
        if not review:
            raise HTTPException(404, "review not found")
        if not review.reviewer_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
        for field, value in review_in.model_dump(
            exclude_unset=True,
        ).items():
            setattr(review, field, value)

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return ReviewResponse.model_validate(review)

    async def delete_review(self, current_user: dict, review_id: str):
        # deleting review
        role_permisison = current_user.role.lower()
        if not role_permisison == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised for this action."
            )
        review = self.db.query(ReviewModel).filter(ReviewModel.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no review found")

        self.db.delete(review)
        self.db.commit()
        return {"message": "review deleted successfully", "id": review_id}


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review_in: ReviewCreateRequest,
    current_user: dict = Depends(get_current_user),
    resource: ReviewResource = Depends(),
) -> ReviewResponse:
    # here
    return await resource.create_review(review_in=review_in, current_user=current_user)


@router.get("/properties/{property_id}/reviews")
async def list_review(
    property_id: str, skip: int = 0, limit: int = 10, resource: ReviewResource = Depends()
):
    # list all review of particular property
    return await resource.list_review(property_id, skip=skip, limit=limit)


@router.get("/reviews/{review_id}")
async def get_review(
    review_id: str,
    resource: ReviewResource = Depends(),
):
    # return review of the particular review id
    return await resource.get_review(review_id)


@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: str,
    resource: ReviewResource = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await resource.delete_review(
        current_user=current_user,
        review_id=review_id,
    )


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_in: ReviewUpdateRequest,
    current_user: dict = Depends(get_current_user),
    resource: ReviewResource = Depends(),
):
    return await resource.update_review(
        review_in=review_in, current_user=current_user, review_id=review_id
    )
