from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from dependencies.db import get_db_session
from dependencies.auth_deps import get_current_user_with_token
from services.user_service import UserService
from models.schemas import UserCreate, UserLogin, UserResponse, Token
from models.user import Position

router = APIRouter(prefix="/auth", tags=["인증"])

# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def register(user_data: UserCreate, db: Session = Depends(get_db_session)):
#     """회원가입"""
#     user_service = UserService(db)
#     new_user = user_service.create_user(user_data)
    
#     return UserResponse(
#         id=new_user.id,
#         login_id=new_user.login_id,
#         name=new_user.name,
#         position=Position(new_user.user_position),
#         created_at=new_user.created_at.isoformat()
#     )

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db_session)):
    """로그인"""
    user_service = UserService(db)
    user = user_service.authenticate_user(login_data)
    access_token = user_service.create_access_token(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(user_and_token = Depends(get_current_user_with_token), db: Session = Depends(get_db_session)):
    """로그아웃"""
    current_user, token = user_and_token
    user_service = UserService(db)
    
    # Redis에서 세션 삭제
    user_id = current_user["sub"]
    success = user_service.logout_user(user_id)
    
    if success:
        return {"message": "성공적으로 로그아웃되었습니다.", "user": current_user["name"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        )
