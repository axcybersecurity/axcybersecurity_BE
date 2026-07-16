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
    
    @classmethod
    def from_notice(cls, notice):
        """Notice 객체에서 NoticeResponse 생성"""
        return cls(
            id=notice.id,
            title=notice.title,
            content=notice.content,
            author=notice.author,
            created_at=notice.created_at.isoformat(),
            view_count=notice.view_count
        )

class NoticeListResponse(BaseModel):
    notices: List[NoticeResponse]
    total: int

# 포스팅 관련 스키마
class PostCreate(BaseModel):
    caption: str  # 캡션/제목
    description: str  # 설명/내용
    author_id: int  # 작성자 ID

class PostUpdate(BaseModel):
    caption: Optional[str] = None
    description: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    caption: str
    description: str
    image_paths: List[str]  # 이미지 파일 경로 리스트
    author_id: int
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_post(cls, post):
        """Post 객체에서 PostResponse 생성"""
        image_paths = []
        for path in post.image_paths or []:
            normalized_path = path.replace("\\", "/").lstrip("/")
            if normalized_path.startswith("api/uploads/"):
                image_paths.append(f"/{normalized_path}")
            elif normalized_path.startswith("uploads/"):
                image_paths.append(f"/api/{normalized_path}")
            else:
                image_paths.append(path)

        return cls(
            id=post.id,
            caption=post.caption,
            description=post.description,
            image_paths=image_paths,
            author_id=post.author_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat() if post.updated_at else None
        )

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
