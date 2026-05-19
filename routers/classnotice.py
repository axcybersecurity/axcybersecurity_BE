# routers/classnotice.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlmodel import Session, select
from typing import List, Optional
from pathlib import Path
from uuid import uuid4
import shutil

from dependencies.db import get_db_session
from dependencies.auth_deps import get_current_user
from models.classnotice import ClassNotice, ClassNoticeFile

router = APIRouter(prefix="/classnotice", tags=["classnotice"])

UPLOAD_DIR = Path("uploads/classnotice")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".ppt", ".pptx", ".pdf", ".hwp", ".hwpx"}


def make_file_url(request: Request, saved_name: str) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/uploads/classnotice/{saved_name}"


def serialize_notice(notice: ClassNotice, files: List[ClassNoticeFile]):
    return {
        "id": notice.id,
        "title": notice.title,
        "content": notice.content,
        "author": notice.author,
        "created_at": notice.created_at.isoformat(),
        "view_count": notice.view_count,
        "files": [
            {
                "id": file.id,
                "original_name": file.original_name,
                "file_url": file.file_url,
                "file_size": file.file_size,
            }
            for file in files
        ],
    }


@router.post("/")
def create_classnotice(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    author_name = current_user["name"]

    notice = ClassNotice(
        title=title,
        content=content,
        author=author_name,
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    saved_files = []

    for upload in files or []:
        original_name = upload.filename
        ext = Path(original_name).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 형식입니다: {original_name}",
            )

        saved_name = f"{uuid4().hex}{ext}"
        save_path = UPLOAD_DIR / saved_name

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

        file_size = save_path.stat().st_size
        file_url = make_file_url(request, saved_name)

        file_record = ClassNoticeFile(
            classnotice_id=notice.id,
            original_name=original_name,
            saved_name=saved_name,
            file_url=file_url,
            file_size=file_size,
        )

        db.add(file_record)
        saved_files.append(file_record)

    db.commit()

    for file_record in saved_files:
        db.refresh(file_record)

    return {
        "notice": serialize_notice(notice, saved_files)
    }


@router.get("/")
def get_classnotices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db_session),
):
    notices = db.exec(
        select(ClassNotice)
        .order_by(ClassNotice.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    total = len(db.exec(select(ClassNotice)).all())

    result = []

    for notice in notices:
        files = db.exec(
            select(ClassNoticeFile).where(ClassNoticeFile.classnotice_id == notice.id)
        ).all()
        result.append(serialize_notice(notice, files))

    return {
        "notices": result,
        "total": total,
    }


@router.get("/{notice_id}")
def get_classnotice(
    notice_id: int,
    db: Session = Depends(get_db_session),
):
    notice = db.get(ClassNotice, notice_id)

    if not notice:
        raise HTTPException(status_code=404, detail="강의자료를 찾을 수 없습니다.")

    notice.view_count += 1
    db.add(notice)
    db.commit()
    db.refresh(notice)

    files = db.exec(
        select(ClassNoticeFile).where(ClassNoticeFile.classnotice_id == notice.id)
    ).all()

    return {
        "notice": serialize_notice(notice, files)
    }


@router.put("/{notice_id}")
def update_classnotice(
    notice_id: int,
    data: dict,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    notice = db.get(ClassNotice, notice_id)

    if not notice:
        raise HTTPException(status_code=404, detail="강의자료를 찾을 수 없습니다.")

    notice.title = data.get("title", notice.title)
    notice.content = data.get("content", notice.content)

    db.add(notice)
    db.commit()
    db.refresh(notice)

    files = db.exec(
        select(ClassNoticeFile).where(ClassNoticeFile.classnotice_id == notice.id)
    ).all()

    return {
        "notice": serialize_notice(notice, files)
    }


@router.delete("/{notice_id}")
def delete_classnotice(
    notice_id: int,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    notice = db.get(ClassNotice, notice_id)

    if not notice:
        raise HTTPException(status_code=404, detail="강의자료를 찾을 수 없습니다.")

    files = db.exec(
        select(ClassNoticeFile).where(ClassNoticeFile.classnotice_id == notice.id)
    ).all()

    for file_record in files:
        file_path = UPLOAD_DIR / file_record.saved_name
        if file_path.exists():
            file_path.unlink()

        db.delete(file_record)

    db.delete(notice)
    db.commit()

    return {
        "message": "강의자료가 삭제되었습니다."
    }