from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt as _bcrypt
from config import settings

class AuthHandler:
    def hash_password(self, password: str) -> str:
        pwd = password.encode('utf-8')[:72]
        return _bcrypt.hashpw(pwd, _bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pwd = plain_password.encode('utf-8')[:72]
            return _bcrypt.checkpw(pwd, hashed_password.encode('utf-8'))
        except Exception:
            return False

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(hours=settings.JWT_EXPIRATION_HOURS))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            return None

auth_handler = AuthHandler()
