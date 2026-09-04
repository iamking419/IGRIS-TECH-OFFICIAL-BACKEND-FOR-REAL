from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    client = Column(String(150), nullable=True)
    category = Column(String(100), nullable=False, default="General")
    year = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="DRAFT")  # DRAFT, PUBLISHED

    # Case-study content fields
    short_description = Column(Text, nullable=True)
    overview = Column(Text, nullable=True)
    challenge = Column(Text, nullable=True)
    approach = Column(Text, nullable=True)
    design = Column(Text, nullable=True)
    development = Column(Text, nullable=True)
    results = Column(Text, nullable=True)

    # Structured arrays
    services = Column(JSON, default=list, nullable=True)
    technologies = Column(JSON, default=list, nullable=True)

    # Project cover image (External URL / CDN link)
    cover_image = Column(String(500), nullable=True)

    # Optional project link
    project_link = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)


class EcosystemProduct(Base):
    __tablename__ = "ecosystem_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    details = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(150), nullable=True)
    role = Column(String(150), nullable=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False, default=5)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(150), nullable=True)
    project_type = Column(String(100), nullable=True)
    timeline = Column(String(100), nullable=True)
    budget = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="NEW")  # NEW, CONTACTED, IN_PROGRESS, COMPLETED, ARCHIVED

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
