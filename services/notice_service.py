from sqlmodel import Session, select
from typing import List, Optional
from models.notice import Notice
from models.schemas import NoticeCreate, NoticeUpdate
from datetime import datetime

class NoticeService:
    def __init__(self, db: Session):
        self.db = db

    def create_notice(self, notice_data: NoticeCreate, author: str) -> Notice:
        """공지사항 생성"""
        notice = Notice(
            title=notice_data.title,
            content=notice_data.content,
            author=author,
            created_at=datetime.utcnow(),
            view_count=0
        )
        self.db.add(notice)
        self.db.commit()
        self.db.refresh(notice)
        return notice

    def get_notice(self, notice_id: int) -> Optional[Notice]:
        """공지사항 조회 (조회수 증가)"""
        statement = select(Notice).where(Notice.id == notice_id)
        notice = self.db.exec(statement).first()
        
        if notice:
            # 조회수 증가
            notice.view_count += 1
            self.db.commit()
            self.db.refresh(notice)
        
        return notice

    def get_notices(self, skip: int = 0, limit: int = 10) -> List[Notice]:
        """공지사항 목록 조회 (최신순)"""
        statement = select(Notice).order_by(Notice.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.exec(statement))

    def get_notices_count(self) -> int:
        """전체 공지사항 개수"""
        statement = select(Notice)
        return len(list(self.db.exec(statement)))

    def update_notice(self, notice_id: int, notice_data: NoticeUpdate) -> Optional[Notice]:
        """공지사항 수정"""
        statement = select(Notice).where(Notice.id == notice_id)
        notice = self.db.exec(statement).first()
        
        if notice:
            if notice_data.title is not None:
                notice.title = notice_data.title
            if notice_data.content is not None:
                notice.content = notice_data.content
            
            self.db.commit()
            self.db.refresh(notice)
        
        return notice

    def delete_notice(self, notice_id: int) -> bool:
        """공지사항 삭제"""
        statement = select(Notice).where(Notice.id == notice_id)
        notice = self.db.exec(statement).first()
        
        if notice:
            self.db.delete(notice)
            self.db.commit()
            return True
        
        return False
