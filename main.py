# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dependencies.db import create_db_and_table
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
# from routers.files import router as files_router
from routers.notice import router as notice_router
from routers.post import router as post_router

app = FastAPI(title="InfoSec Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://accs.pusan.ac.kr",
    "http://accs.pusan.ac.kr",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
    ],  # 또는 Unity 실행 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (이미지 파일 접근용)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 라우터 등록
app.include_router(auth_router)
# app.include_router(files_router)
app.include_router(notice_router)
app.include_router(post_router)

@app.on_event("startup")
def on_startup():
    create_db_and_table()
