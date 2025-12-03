from sqlmodel import Session, select
from typing import List, Optional
from models.post import Post
from models.schemas import PostCreate, PostUpdate
from datetime import datetime

class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, caption: str, description: str, image_path: str, author_id: int) -> Post:
        """포스팅 생성"""
        post = Post(
            caption=caption,
            description=description,
            image_path=image_path,
            author_id=author_id,
            created_at=datetime.utcnow()
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        """포스팅 조회"""
        statement = select(Post).where(Post.id == post_id)
        return self.db.exec(statement).first()

    def get_posts(self, skip: int = 0, limit: int = 10) -> List[Post]:
        """포스팅 목록 조회 (최신순)"""
        statement = select(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.exec(statement))

    def get_posts_count(self) -> int:
        """전체 포스팅 개수"""
        statement = select(Post)
        return len(list(self.db.exec(statement)))

    def update_post(self, post_id: int, post_data: PostUpdate, image_path: Optional[str] = None) -> Optional[Post]:
        """포스팅 수정"""
        statement = select(Post).where(Post.id == post_id)
        post = self.db.exec(statement).first()
        
        if post:
            if post_data.caption is not None:
                post.caption = post_data.caption
            if post_data.description is not None:
                post.description = post_data.description
            if image_path is not None:
                post.image_path = image_path
            post.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(post)
        
        return post

    def delete_post(self, post_id: int) -> bool:
        """포스팅 삭제"""
        statement = select(Post).where(Post.id == post_id)
        post = self.db.exec(statement).first()
        
        if post:
            self.db.delete(post)
            self.db.commit()
            return True
        
        return False

