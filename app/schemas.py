from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models import DocType, ProjectStatus, SourceFormat


# --- Auth ---

class AuthRequest(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    name: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Projects ---

class ProjectCreate(BaseModel):
    name: str
    client_name: Optional[str] = None
    status: ProjectStatus = ProjectStatus.active


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(BaseModel):
    id: int
    owner_id: int
    name: str
    client_name: Optional[str]
    status: ProjectStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Segments ---

class SegmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SegmentRead(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Products ---

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None


class ProductRead(BaseModel):
    id: int
    segment_id: int
    name: str
    description: Optional[str]
    price: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Documents ---

class DocumentMeta(BaseModel):
    id: int
    project_id: int
    doc_type: DocType
    title: Optional[str]
    original_filename: Optional[str]
    source_format: Optional[SourceFormat]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentRead(DocumentMeta):
    extracted_text: Optional[str]
