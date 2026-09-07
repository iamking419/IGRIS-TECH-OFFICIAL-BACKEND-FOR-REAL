from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


# -----------------------------------------------------------------------------
# Public Endpoints
# -----------------------------------------------------------------------------

@router.get("", response_model=List[schemas.ReviewPublicResponse])
def list_approved_reviews(db: Session = Depends(get_db)):
    """Retrieve list of all approved client testimonials."""
    return (
        db.query(models.Review)
        .filter(models.Review.status == "APPROVED")
        .order_by(models.Review.id.desc())
        .all()
    )


@router.post(
    "",
    response_model=schemas.ReviewPublicResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_review(review_in: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """Public submission of a review (Created in PENDING status, awaiting admin moderation)."""
    review = models.Review(
        name=review_in.name,
        company=review_in.company,
        role=review_in.role,
        content=review_in.content,
        rating=review_in.rating,
        status="PENDING",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# -----------------------------------------------------------------------------
# Admin Protected Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "/admin",
    response_model=List[schemas.ReviewAdminResponse],
    dependencies=[Depends(get_current_admin)],
)
def list_all_reviews_admin(
    status_filter: Optional[schemas.ReviewStatusType] = Query(
        None, alias="status", description="Filter reviews by status (PENDING, APPROVED, REJECTED)"
    ),
    db: Session = Depends(get_db),
):
    """Retrieve all reviews with status and moderation metadata (Admin protected)."""
    query = db.query(models.Review)
    if status_filter:
        query = query.filter(models.Review.status == status_filter)
    return query.order_by(models.Review.id.desc()).all()


@router.patch(
    "/{review_id}",
    response_model=schemas.ReviewAdminResponse,
    dependencies=[Depends(get_current_admin)],
)
def update_review(
    review_id: int,
    review_in: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
):
    """Moderate review status (APPROVE, REJECT) or update review details (Admin protected)."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )

    update_data = review_in.model_dump(exclude_unset=True)

    # Set approved_at timestamp on approval
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "APPROVED" and review.status != "APPROVED":
            review.approved_at = datetime.now(timezone.utc)
        elif new_status != "APPROVED":
            review.approved_at = None

    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review submission (Admin protected)."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )

    db.delete(review)
    db.commit()
    return None
