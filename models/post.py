from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    caption: str = Field(index=True)  # 캡션/제목
    description: str  # 설명/내용
    image_paths: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # 이미지 파일 경로 리스트
    author_id: int = Field(index=True)  # 작성자 ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

