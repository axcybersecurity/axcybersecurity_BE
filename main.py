# main.py
from fastapi import FastAPI
from dependencies.db import create_db_and_table
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.files import router as files_router
from routers.notice import router as notice_router

app = FastAPI(title="InfoSec Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 Unity 실행 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(notice_router)

@app.on_event("startup")
def on_startup():
    create_db_and_table()
