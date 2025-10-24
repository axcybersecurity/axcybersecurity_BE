from pydantic import BaseModel
from typing import Optional, List
from .user import Position

class UserCreate(BaseModel):
    login_id: str
    password: str
    name: str
    position: Position

class UserLogin(BaseModel):
    login_id: str
    password: str

class UserResponse(BaseModel):
    id: int
    login_id: str
    name: str
    position: Position
    created_at: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# File Station 관련 스키마
class FileItem(BaseModel):
    path: str
    name: str
    isdir: bool
    size: Optional[int] = None
    owner: Optional[str] = None
    time: Optional[int] = None

class FileListResponse(BaseModel):
    files: List[FileItem]
    total: int
    offset: int
    limit: int

# 공지사항 관련 스키마
class NoticeCreate(BaseModel):
    title: str
    content: str
    author: str

class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str
    view_count: int

    class Config:
        from_attributes = True

class NoticeListResponse(BaseModel):
    notices: List[NoticeResponse]
    total: int