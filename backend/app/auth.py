from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User


# ---------- 密码哈希 ----------

# passlib 是 Python 的密码哈希库，支持多种算法
# 我们用 bcrypt，它是目前最安全的密码哈希算法之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """把明文密码哈希成密文"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和哈希值是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT Token ----------

# OAuth2PasswordBearer 会从请求头的 Authorization: Bearer <token> 中提取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT Token

    JWT 的结构：header.payload.signature
    payload 里一般存用户标识（这里是 user_id）和过期时间
    """
    to_encode = {"sub": str(subject)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Token 中获取当前登录用户（FastAPI 依赖注入用）

    接口函数里声明 `current_user: User = Depends(get_current_user)`，
    FastAPI 会自动解析 Token、查用户、验证有效性。
    如果 Token 无效或用户不存在，直接抛 401 未授权错误。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的凭证或登录已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 根据 ID 查用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user
