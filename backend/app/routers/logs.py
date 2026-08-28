from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OperationLog
from app.auth import get_current_user

router = APIRouter(prefix="/api/logs", tags=["操作日志"])

@router.get("", summary="查询操作日志")
def list_logs(
    target_type: Optional[str] = Query(None, description="对象类型：transfer/file/user..."),
    target_id: Optional[int] = Query(None, description="对象ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(OperationLog)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    if target_id:
        query = query.filter(OperationLog.target_id == target_id)
    total = query.count()
    items = (
        query.order_by(OperationLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": items}