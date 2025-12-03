# db.py
from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv
# 모든 모델을 import하여 테이블이 생성되도록 함
from models.user import User
from models.notice import Notice
from models.post import Post

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
DB_ENGINE = create_engine(DB_URL, echo=True)

def get_db_session():
    with Session(DB_ENGINE) as sess:
        yield sess

def create_db_and_table():
    SQLModel.metadata.create_all(DB_ENGINE)