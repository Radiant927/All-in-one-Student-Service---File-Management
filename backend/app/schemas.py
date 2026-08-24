from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models import Campus, TransferStatus, FileType, Urgency


# ---------- 用户相关 ----------

class UserLogin(BaseModel):
    """登录请求体"""
    username: str
    password: str


class UserBase(BaseModel):
    username: str
    real_name: str
    campus: Campus
    phone: str = ""
    is_admin: bool = False


class UserResponse(UserBase):
    """返回给前端的用户信息（不含密码）"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # 可以直接从 SQLAlchemy 对象转换


class Token(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)


# ---------- 转交单相关 ----------

class TransferFileResponse(BaseModel):
    """附件信息"""
    id: int
    original_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    """发起转交单请求体"""
    title: str
    description: str = ""
    courier_name: str
    courier_phone: str = ""
    receiver_name: str
    receiver_phone: str = ""
    depart_time: datetime
    estimate_arrive_time: Optional[datetime] = None
    to_campus: Campus
    file_type: FileType = FileType.OTHER
    urgency: Urgency = Urgency.NORMAL
    file_ids: List[int] = []  # 上传后的文件ID列表


class TransferUpdate(BaseModel):
    """编辑转交单"""
    title: Optional[str] = None
    description: Optional[str] = None
    courier_name: Optional[str] = None
    courier_phone: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    depart_time: Optional[datetime] = None
    estimate_arrive_time: Optional[datetime] = None
    file_type: Optional[FileType] = None
    urgency: Optional[Urgency] = None
    file_ids: Optional[List[int]] = None


class TransferResponse(BaseModel):
    """转交单详情响应"""
    id: int
    transfer_no: str
    title: str
    description: str
    courier_name: str
    courier_phone: str
    receiver_name: str
    receiver_phone: str
    depart_time: datetime
    estimate_arrive_time: Optional[datetime] = None
    confirm_time: Optional[datetime] = None
    from_campus: Campus
    to_campus: Campus
    file_type: FileType
    urgency: Urgency
    status: TransferStatus
    confirm_message: str
    exception_note: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    files: List[TransferFileResponse] = []

    class Config:
        from_attributes = True


class TransferListResponse(BaseModel):
    """转交单列表（带分页）"""
    total: int
    page: int
    page_size: int
    items: List[TransferResponse]


class ConfirmTransfer(BaseModel):
    """确认收到"""
    message: str = ""


class ReportException(BaseModel):
    """上报异常"""
    note: str


# ---------- 校车班次 ----------

class BusScheduleCreate(BaseModel):
    name: str
    from_campus: Campus
    to_campus: Campus
    depart_time: str
    arrive_time: str
    sort_order: int = 0


class BusScheduleUpdate(BaseModel):
    name: Optional[str] = None
    from_campus: Optional[Campus] = None
    to_campus: Optional[Campus] = None
    depart_time: Optional[str] = None
    arrive_time: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class BusScheduleResponse(BaseModel):
    id: int
    name: str
    from_campus: Campus
    to_campus: Campus
    depart_time: str
    arrive_time: str
    is_active: bool
    sort_order: int

    class Config:
        from_attributes = True


# ---------- 统计 ----------

class DashboardStats(BaseModel):
    """首页统计数据"""
    pending_receive: int       # 待我接收
    my_pending_confirm: int    # 我发起的待确认
    total_this_month: int      # 本月总数
    confirmed_this_month: int  # 本月已确认
