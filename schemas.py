from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -----------------------------------------------------------------------------
# Project Schemas
# -----------------------------------------------------------------------------

ProjectStatusType = Literal["DRAFT", "PUBLISHED"]


class ProjectBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    client: Optional[str] = None
    category: str = "General"
    year: Optional[int] = None
    short_description: Optional[str] = None
    overview: Optional[str] = None
    challenge: Optional[str] = None
    approach: Optional[str] = None
    design: Optional[str] = None
    development: Optional[str] = None
    results: Optional[str] = None
    cover_image: Optional[str] = None
    services: Optional[List[str]] = Field(default_factory=list)
    technologies: Optional[List[str]] = Field(default_factory=list)
    project_link: Optional[str] = None


class ProjectCreate(ProjectBase):
    status: Optional[ProjectStatusType] = "DRAFT"


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    client: Optional[str] = None
    category: Optional[str] = None
    year: Optional[int] = None
    status: Optional[ProjectStatusType] = None
    short_description: Optional[str] = None
    overview: Optional[str] = None
    challenge: Optional[str] = None
    approach: Optional[str] = None
    design: Optional[str] = None
    development: Optional[str] = None
    results: Optional[str] = None
    cover_image: Optional[str] = None
    services: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    project_link: Optional[str] = None


class ProjectPublicResponse(ProjectBase):
    """Public case-study project response schema."""
    model_config = ConfigDict(from_attributes=True)


class ProjectAdminResponse(ProjectBase):
    """Full admin project response schema with status and timestamps."""
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Ecosystem Schemas
# -----------------------------------------------------------------------------

EcosystemStatusType = Literal["ACTIVE", "INACTIVE"]


class EcosystemBase(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    details: str
    link: Optional[str] = None
    status: Optional[EcosystemStatusType] = "ACTIVE"


class EcosystemCreate(EcosystemBase):
    pass


class EcosystemUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    details: Optional[str] = None
    link: Optional[str] = None
    status: Optional[EcosystemStatusType] = None


class EcosystemResponse(EcosystemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Review Schemas
# -----------------------------------------------------------------------------

ReviewStatusType = Literal["PENDING", "APPROVED", "REJECTED"]


class ReviewCreate(BaseModel):
    name: str = Field(..., max_length=100)
    company: Optional[str] = None
    role: Optional[str] = None
    content: str
    rating: int = Field(5, ge=1, le=5, description="Rating from 1 to 5")


class ReviewPublicResponse(BaseModel):
    id: int
    name: str
    company: Optional[str] = None
    role: Optional[str] = None
    content: str
    rating: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewAdminResponse(BaseModel):
    id: int
    name: str
    company: Optional[str] = None
    role: Optional[str] = None
    content: str
    rating: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[ReviewStatusType] = None


# -----------------------------------------------------------------------------
# Contact Submission Schemas
# -----------------------------------------------------------------------------

ContactStatusType = Literal["NEW", "CONTACTED", "IN_PROGRESS", "COMPLETED", "ARCHIVED"]


class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    company: Optional[str] = None
    project_type: Optional[str] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    description: str


class ContactSubmissionResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: Optional[str] = None
    project_type: Optional[str] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    description: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ContactSubmissionUpdate(BaseModel):
    status: Optional[ContactStatusType] = None
