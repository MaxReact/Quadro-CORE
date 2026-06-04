import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_owned_document, get_owned_project
from app.models import DocType, ProjectDocument, SourceFormat, Project
from app.schemas import DocumentMeta, DocumentRead
from app.services.extractors import extract
from app.storage import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, delete_file, save_file

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

_EXT_TO_FORMAT: dict[str, SourceFormat] = {
    "xlsx": SourceFormat.xlsx,
    "docx": SourceFormat.docx,
    "xmind": SourceFormat.xmind,
    "txt": SourceFormat.txt,
    "md": SourceFormat.md,
}


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile,
    doc_type: DocType = Form(...),
    title: Optional[str] = Form(None),
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
) -> ProjectDocument:
    # --- Validate extension ---
    ext = Path(file.filename or "").suffix.lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла '{ext}'. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # --- Validate size (read all at once, bounded) ---
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой ({len(data) // 1024 // 1024} МБ). Максимум 20 МБ.",
        )

    # --- Save to disk ---
    file_path = save_file(project.id, file.filename or f"file.{ext}", data)

    # --- Extract text ---
    abs_path = str(Path(__file__).parent.parent.parent / file_path)
    extracted_text = extract(abs_path, ext)

    # --- Persist ---
    doc = ProjectDocument(
        project_id=project.id,
        doc_type=doc_type,
        title=title or file.filename,
        original_filename=file.filename,
        file_path=file_path,
        source_format=_EXT_TO_FORMAT.get(ext),
        extracted_text=extracted_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/projects/{project_id}/documents", response_model=list[DocumentMeta])
def list_documents(
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
) -> list[ProjectDocument]:
    return (
        db.query(ProjectDocument)
        .filter(ProjectDocument.project_id == project.id)
        .all()
    )


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(doc: ProjectDocument = Depends(get_owned_document)) -> ProjectDocument:
    return doc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc: ProjectDocument = Depends(get_owned_document),
    db: Session = Depends(get_db),
) -> None:
    if doc.file_path:
        delete_file(doc.file_path)
    db.delete(doc)
    db.commit()
