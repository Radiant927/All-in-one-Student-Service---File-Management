from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Transfer
from app.auth import get_current_user
from app.services import notification


router = APIRouter(prefix="/api/notification", tags=["通知测试"])


@router.post("/test", summary="测试微信通知（管理员）")
def test_notification(
    content: str = "这是一条来自文件交接系统的测试消息",
    current_user: User = Depends(get_current_user),
):
    """发送一条测试消息到企业微信群，验证 Webhook 是否配置正确"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    success = notification.send_text(content)
    if success:
        return {"message": "通知发送成功"}
    else:
        return {
            "message": "通知未发送",
            "reason": "可能未配置 WECHAT_WEBHOOK_URL，或网络不通",
        }
