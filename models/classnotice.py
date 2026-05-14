from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ClassNotice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author: str
    view_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClassNoticeFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    classnotice_id: int = Field(foreign_key="classnotice.id")
    original_name: str
    saved_name: str
    file_url: str
    file_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)