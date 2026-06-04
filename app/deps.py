from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Product, Project, Segment, User
from app.security import decode_access_token

_bearer = HTTPBearer()

_404 = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# --- Ownership resolvers ---
# Always return 404 (not 403) to avoid leaking existence of other users' objects.

def get_owned_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        raise _404
    return project


def get_owned_segment(
    segment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Segment:
    segment = db.get(Segment, segment_id)
    if segment is None:
        raise _404
    project = db.get(Project, segment.project_id)
    if project is None or project.owner_id != current_user.id:
        raise _404
    return segment


def get_owned_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise _404
    segment = db.get(Segment, product.segment_id)
    if segment is None:
        raise _404
    project = db.get(Project, segment.project_id)
    if project is None or project.owner_id != current_user.id:
        raise _404
    return product
