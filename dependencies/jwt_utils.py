#app/dependencies/jwt_utils.py
from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "1234")  # 기본값으로 임시값 사용
ALG = os.getenv("ALGORITHM", "HS256")


class JWTUtil:
    # 1. JWT 토큰 생성 함수
    def create_token(self, payload: Dict, expires_delta: Optional[timedelta] = timedelta(minutes=30)):
        payload_to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        payload_to_encode.update({"exp": expire})
        return jwt.encode(payload_to_encode, SECRET_KEY, algorithm=ALG)

    # 2. token 문자열로 payload 만드는 함수
    def decode_token(self, token: str) -> Optional[Dict]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALG])
        except Exception:
            return None