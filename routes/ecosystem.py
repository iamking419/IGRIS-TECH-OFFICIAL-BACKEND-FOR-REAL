from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import require_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/ecosystem", tags=["Ecosystem"])


# -----------------------------------------------------------------------------
# Public Endpoints
# -----------------------------------------------------------------------------

@router.get("", response_model=List[schemas.EcosystemResponse])
def list_active_ecosystem_products(db: Session = Depends(get_db)):
    """Retrieve list of all active ecosystem tools and products."""
    return (
        db.query(models.EcosystemProduct)
        .filter(models.EcosystemProduct.status == "ACTIVE")
        .order_by(models.EcosystemProduct.id.asc())
        .all()
    )


@router.get("/{slug}", response_model=schemas.EcosystemResponse)
def get_ecosystem_product_by_slug(slug: str, db: Session = Depends(get_db)):
    """Retrieve a single active ecosystem product by its slug."""
    product = (
        db.query(models.EcosystemProduct)
        .filter(
            models.EcosystemProduct.slug == slug,
            models.EcosystemProduct.status == "ACTIVE",
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ecosystem product '{slug}' not found or is inactive",
        )
    return product


# -----------------------------------------------------------------------------
# Admin Protected Endpoints
# -----------------------------------------------------------------------------

@router.post(
    "",
    response_model=schemas.EcosystemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_ecosystem_product(
    product_in: schemas.EcosystemCreate, db: Session = Depends(get_db)
):
    """Create a new ecosystem product (Admin protected)."""
    existing = (
        db.query(models.EcosystemProduct)
        .filter(models.EcosystemProduct.slug == product_in.slug)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ecosystem product with slug '{product_in.slug}' already exists",
        )

    product = models.EcosystemProduct(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch(
    "/{product_id}",
    response_model=schemas.EcosystemResponse,
    dependencies=[Depends(require_admin)],
)
def update_ecosystem_product(
    product_id: int,
    product_in: schemas.EcosystemUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing ecosystem product (Admin protected)."""
    product = db.query(models.EcosystemProduct).filter(models.EcosystemProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ecosystem product with ID {product_id} not found",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != product.slug:
        existing = (
            db.query(models.EcosystemProduct)
            .filter(models.EcosystemProduct.slug == update_data["slug"])
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ecosystem product with slug '{update_data['slug']}' already exists",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_ecosystem_product(product_id: int, db: Session = Depends(get_db)):
    """Delete an ecosystem product (Admin protected)."""
    product = db.query(models.EcosystemProduct).filter(models.EcosystemProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ecosystem product with ID {product_id} not found",
        )

    db.delete(product)
    db.commit()
    return None
