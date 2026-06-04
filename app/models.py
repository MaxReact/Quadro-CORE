import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    pm = "pm"
    marketer = "marketer"
    client = "client"


class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class DocType(str, enum.Enum):
    custdev = "custdev"
    swot = "swot"
    four_p = "4p"
    creative = "creative"
    offer = "offer"
    other = "other"


class SourceFormat(str, enum.Enum):
    xlsx = "xlsx"
    docx = "docx"
    xmind = "xmind"
    txt = "txt"
    md = "md"


class GenType(str, enum.Enum):
    offer = "offer"
    creative_text = "creative_text"
    headlines = "headlines"


class GenStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.admin, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="owner", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.active, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    segments: Mapped[list["Segment"]] = relationship(
        "Segment", back_populates="project", cascade="all, delete-orphan"
    )
    documents: Mapped[list["ProjectDocument"]] = relationship(
        "ProjectDocument", back_populates="project", cascade="all, delete-orphan"
    )
    generations: Mapped[list["Generation"]] = relationship(
        "Generation", back_populates="project", cascade="all, delete-orphan"
    )


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="segments")
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="segment", cascade="all, delete-orphan"
    )
    generations: Mapped[list["Generation"]] = relationship(
        "Generation", back_populates="segment"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("segments.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    segment: Mapped["Segment"] = relationship("Segment", back_populates="products")
    generations: Mapped[list["Generation"]] = relationship(
        "Generation", back_populates="product"
    )


class ProjectDocument(Base):
    __tablename__ = "project_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(512))
    source_format: Mapped[Optional[SourceFormat]] = mapped_column(Enum(SourceFormat))
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="documents")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    segment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("segments.id"), nullable=True
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True
    )
    gen_type: Mapped[GenType] = mapped_column(Enum(GenType), nullable=False)
    brief: Mapped[Optional[str]] = mapped_column(Text)
    variants: Mapped[Optional[dict]] = mapped_column(JSON)
    selected_variant_index: Mapped[Optional[int]] = mapped_column(Integer)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    image_template_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[GenStatus] = mapped_column(
        Enum(GenStatus), default=GenStatus.draft, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="generations")
    segment: Mapped[Optional["Segment"]] = relationship(
        "Segment", back_populates="generations"
    )
    product: Mapped[Optional["Product"]] = relationship(
        "Product", back_populates="generations"
    )
