from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, get_owned_project, get_owned_segment
from app.models import Project, Segment, User
from app.schemas import SegmentCreate, SegmentRead, SegmentUpdate

router = APIRouter(tags=["segments"])


@router.get("/projects/{project_id}/segments", response_model=list[SegmentRead])
def list_segments(
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
) -> list[Segment]:
    return db.query(Segment).filter(Segment.project_id == project.id).all()


@router.post(
    "/projects/{project_id}/segments",
    response_model=SegmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_segment(
    body: SegmentCreate,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
) -> Segment:
    segment = Segment(project_id=project.id, **body.model_dump())
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment


@router.patch("/segments/{segment_id}", response_model=SegmentRead)
def update_segment(
    body: SegmentUpdate,
    segment: Segment = Depends(get_owned_segment),
    db: Session = Depends(get_db),
) -> Segment:
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(segment, field, value)
    db.commit()
    db.refresh(segment)
    return segment


@router.delete("/segments/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_segment(
    segment: Segment = Depends(get_owned_segment),
    db: Session = Depends(get_db),
) -> None:
    db.delete(segment)
    db.commit()
