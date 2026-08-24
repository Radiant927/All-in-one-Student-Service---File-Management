from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserLogin, Token, UserResponse, PasswordChange
from app.auth import verify_password, create_access_token, get_current_user, hash_password


router = APIRouter(prefix="/api/auth", tags=["鉴权"])


@router.post("/login", response_model=Token, summary="用户登录")
def login(form: UserLogin, db: Session = Depends(get_db)):
    """用户登录，返回 JWT Token 和用户信息"""
    # 1. 根据用户名查用户
    user = db.query(User).filter(User.username == form.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 2. 验证密码
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 3. 检查账户是否启用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用",
        )

    # 4. 生成 Token
    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse, summary="获取当前登录用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """根据 Token 获取当前用户信息"""
    return current_user


@router.post("/change-password", summary="修改密码")
def change_password(
    form: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码"""
    # 验证旧密码
    if not verify_password(form.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确",
        )

    # 更新密码
    current_user.hashed_password = hash_password(form.new_password)
    db.commit()

    return {"message": "密码修改成功"}
