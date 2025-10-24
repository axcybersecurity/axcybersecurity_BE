from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from dependencies.db import get_db_session
from dependencies.auth_deps import get_current_user
from services.notice_service import NoticeService
from models.schemas import NoticeCreate, NoticeUpdate, NoticeResponse, NoticeListResponse

router = APIRouter(prefix="/notices", tags=["notices"])

@router.post("/", response_model=NoticeResponse)
def create_notice(
    notice_data: NoticeCreate, 
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """공지사항 생성"""
    notice_service = NoticeService(db)
    author_name = current_user["name"]  # JWT에서 사용자 이름 가져오기
    notice = notice_service.create_notice(notice_data, author_name)
    return NoticeResponse.from_notice(notice)

@router.get("/", response_model=NoticeListResponse)
def get_notices(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(10, ge=1, le=100, description="가져올 개수"),
    db: Session = Depends(get_db_session)
):
    """공지사항 목록 조회"""
    notice_service = NoticeService(db)
    notices = notice_service.get_notices(skip=skip, limit=limit)
    total = notice_service.get_notices_count()
    
    # Notice 객체들을 NoticeResponse로 변환
    notice_responses = [NoticeResponse.from_notice(notice) for notice in notices]
    
    return NoticeListResponse(notices=notice_responses, total=total)

@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(notice_id: int, db: Session = Depends(get_db_session)):
    """공지사항 상세 조회 (조회수 증가)"""
    notice_service = NoticeService(db)
    notice = notice_service.get_notice(notice_id)
    
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    return NoticeResponse.from_notice(notice)

@router.put("/{notice_id}", response_model=NoticeResponse)
def update_notice(
    notice_id: int, 
    notice_data: NoticeUpdate, 
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """공지사항 수정"""
    notice_service = NoticeService(db)
    notice = notice_service.update_notice(notice_id, notice_data)
    
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    return NoticeResponse.from_notice(notice)

@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int, 
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """공지사항 삭제"""
    notice_service = NoticeService(db)
    success = notice_service.delete_notice(notice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    return {"message": "공지사항이 삭제되었습니다"}
