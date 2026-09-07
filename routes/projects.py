from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


# -----------------------------------------------------------------------------
# Public Endpoints
# -----------------------------------------------------------------------------

@router.get("", response_model=List[schemas.ProjectPublicResponse])
def list_published_projects(
    category: Optional[str] = Query(None, description="Filter projects by category"),
    db: Session = Depends(get_db),
):
    """Retrieve list of all published projects for the public showcase."""
    query = db.query(models.Project).filter(models.Project.status == "PUBLISHED")
    if category:
        query = query.filter(models.Project.category.ilike(f"%{category}%"))

    return query.order_by(models.Project.year.desc().nullslast(), models.Project.id.desc()).all()


@router.get("/{slug}", response_model=schemas.ProjectPublicResponse)
def get_published_project_by_slug(slug: str, db: Session = Depends(get_db)):
    """Retrieve a single published project by its unique slug."""
    project = (
        db.query(models.Project)
        .filter(models.Project.slug == slug, models.Project.status == "PUBLISHED")
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{slug}' not found or is unpublished",
        )
    return project


# -----------------------------------------------------------------------------
# Admin Protected Endpoints
# -----------------------------------------------------------------------------

@router.post(
    "",
    response_model=schemas.ProjectAdminResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project (Admin protected)."""
    existing = db.query(models.Project).filter(models.Project.slug == project_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A project with slug '{project_in.slug}' already exists",
        )

    data = project_in.model_dump()
    if data.get("status") == "PUBLISHED":
        data["published_at"] = datetime.now(timezone.utc)

    project = models.Project(**data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch(
    "/{project_id}",
    response_model=schemas.ProjectAdminResponse,
    dependencies=[Depends(get_current_admin)],
)
def update_project(
    project_id: int,
    project_in: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update project details or publication status (Admin protected)."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    update_data = project_in.model_dump(exclude_unset=True)

    # Validate slug uniqueness if changed
    if "slug" in update_data and update_data["slug"] != project.slug:
        existing = (
            db.query(models.Project)
            .filter(models.Project.slug == update_data["slug"])
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A project with slug '{update_data['slug']}' already exists",
            )

    # Manage published_at timestamp
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "PUBLISHED" and project.status != "PUBLISHED":
            project.published_at = datetime.now(timezone.utc)
        elif new_status == "DRAFT":
            project.published_at = None

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project (Admin protected)."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    db.delete(project)
    db.commit()
    return None
