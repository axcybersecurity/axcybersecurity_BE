from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlmodel import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path
from dependencies.db import get_db_session
from dependencies.auth_deps import get_current_user
from services.post_service import PostService
from models.schemas import PostCreate, PostUpdate, PostResponse, PostListResponse

router = APIRouter(prefix="/posts", tags=["posts"])

# 업로드 디렉토리 설정
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def save_uploaded_file(file: UploadFile) -> str:
    """업로드된 파일을 저장하고 경로를 반환"""
    # 파일 확장자 확인
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"지원하지 않는 이미지 형식입니다. 허용된 형식: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # 고유한 파일명 생성
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # 상대 경로 반환 (DB에 저장)
    return str(file_path)

@router.post("/", response_model=PostResponse)
async def create_post(
    images: List[UploadFile] = File(..., description="이미지 파일들 (여러 개 가능)"),
    caption: str = Form(..., description="캡션/제목"),
    description: str = Form(..., description="설명/내용"),
    author_id: int = Form(..., description="작성자 ID"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """포스팅 생성 (multipart/form-data) - 여러 이미지 지원"""
    # 이미지 파일들 저장
    image_paths = []
    try:
        for image in images:
            image_path = save_uploaded_file(image)
            image_paths.append(image_path)
    except HTTPException:
        raise
    except Exception as e:
        # 저장 실패한 파일들 정리
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")
    
    if not image_paths:
        raise HTTPException(status_code=400, detail="최소 하나의 이미지 파일이 필요합니다")
    
    # 포스팅 생성
    post_service = PostService(db)
    post = post_service.create_post(
        caption=caption,
        description=description,
        image_paths=image_paths,
        author_id=author_id
    )
    
    return PostResponse.from_post(post)

@router.get("/", response_model=PostListResponse)
def get_posts(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(10, ge=1, le=100, description="가져올 개수"),
    db: Session = Depends(get_db_session)
):
    """포스팅 목록 조회"""
    post_service = PostService(db)
    posts = post_service.get_posts(skip=skip, limit=limit)
    total = post_service.get_posts_count()
    
    post_responses = [PostResponse.from_post(post) for post in posts]
    
    return PostListResponse(posts=post_responses, total=total)

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db_session)):
    """포스팅 상세 조회"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="포스팅을 찾을 수 없습니다")
    
    return PostResponse.from_post(post)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    caption: Optional[str] = Form(None, description="캡션/제목"),
    description: Optional[str] = Form(None, description="설명/내용"),
    images: Optional[List[UploadFile]] = File(None, description="이미지 파일들 (선택사항, 여러 개 가능)"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """포스팅 수정 - 여러 이미지 지원"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="포스팅을 찾을 수 없습니다")
    
    # 업데이트 데이터 준비
    post_data = PostUpdate(
        caption=caption,
        description=description
    )
    
    # 이미지 파일들이 제공된 경우 저장
    image_paths = None
    if images:
        new_image_paths = []
        try:
            for image in images:
                image_path = save_uploaded_file(image)
                new_image_paths.append(image_path)
            
            # 기존 이미지 파일들 삭제 (선택사항)
            if post.image_paths:
                for old_path in post.image_paths:
                    if old_path and os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass  # 삭제 실패해도 계속 진행
            
            image_paths = new_image_paths
        except HTTPException:
            # 저장 실패한 파일들 정리
            for path in new_image_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except:
                    pass
            raise
        except Exception as e:
            # 저장 실패한 파일들 정리
            for path in new_image_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")
    
    updated_post = post_service.update_post(post_id, post_data, image_paths)
    
    return PostResponse.from_post(updated_post)

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user) #얘가 Redis임
):
    """포스팅 삭제"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="포스팅을 찾을 수 없습니다")
    
    # 이미지 파일들 삭제
    if post.image_paths:
        for image_path in post.image_paths:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except:
                    pass  # 삭제 실패해도 계속 진행
    
    success = post_service.delete_post(post_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="포스팅을 찾을 수 없습니다")
    
    return {"message": "포스팅이 삭제되었습니다"}

