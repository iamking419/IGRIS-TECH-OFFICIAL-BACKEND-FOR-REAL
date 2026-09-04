from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from auth import require_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/contact", tags=["Contact"])


# -----------------------------------------------------------------------------
# Public Endpoints
# -----------------------------------------------------------------------------

@router.post(
    "",
    response_model=schemas.ContactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_contact_inquiry(
    inquiry_in: schemas.ContactSubmissionCreate, db: Session = Depends(get_db)
):
    """Submit a contact or project inquiry form."""
    submission = models.ContactSubmission(
        name=inquiry_in.name,
        email=inquiry_in.email,
        company=inquiry_in.company,
        project_type=inquiry_in.project_type,
        timeline=inquiry_in.timeline,
        budget=inquiry_in.budget,
        description=inquiry_in.description,
        status="NEW",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# -----------------------------------------------------------------------------
# Admin Protected Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[schemas.ContactSubmissionResponse],
    dependencies=[Depends(require_admin)],
)
def list_contact_inquiries(
    status_filter: Optional[schemas.ContactStatusType] = Query(
        None, alias="status", description="Filter inquiries by status"
    ),
    db: Session = Depends(get_db),
):
    """Retrieve all contact inquiries (Admin protected)."""
    query = db.query(models.ContactSubmission)
    if status_filter:
        query = query.filter(models.ContactSubmission.status == status_filter)
    return query.order_by(models.ContactSubmission.id.desc()).all()


@router.get(
    "/{submission_id}",
    response_model=schemas.ContactSubmissionResponse,
    dependencies=[Depends(require_admin)],
)
def get_contact_inquiry(submission_id: int, db: Session = Depends(get_db)):
    """Retrieve a single contact inquiry by ID (Admin protected)."""
    submission = (
        db.query(models.ContactSubmission)
        .filter(models.ContactSubmission.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquiry with ID {submission_id} not found",
        )
    return submission


@router.patch(
    "/{submission_id}",
    response_model=schemas.ContactSubmissionResponse,
    dependencies=[Depends(require_admin)],
)
def update_contact_inquiry_status(
    submission_id: int,
    status_in: schemas.ContactSubmissionUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of an inquiry (Admin protected)."""
    submission = (
        db.query(models.ContactSubmission)
        .filter(models.ContactSubmission.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquiry with ID {submission_id} not found",
        )

    if status_in.status is not None:
        submission.status = status_in.status

    db.commit()
    db.refresh(submission)
    return submission


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_contact_inquiry(submission_id: int, db: Session = Depends(get_db)):
    """Delete a contact inquiry (Admin protected)."""
    submission = (
        db.query(models.ContactSubmission)
        .filter(models.ContactSubmission.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquiry with ID {submission_id} not found",
        )

    db.delete(submission)
    db.commit()
    return None
