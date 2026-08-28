from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models import Campus, TransferStatus, FileType, Urgency

class UserLogin(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    username: str
    real_name: str
    campus: Campus
    phone: str = ""
    is_admin: bool = False

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)

class TransferFileResponse(BaseModel):
    id: int
    original_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    class Config:
        from_attributes = True

class TransferCreate(BaseModel):
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
    file_ids: List[int] = []

class TransferUpdate(BaseModel):
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
    total: int
    page: int
    page_size: int
    items: List[TransferResponse]

class ConfirmTransfer(BaseModel):
    message: str = ""
    file_ids: List[int] = []

class ReportException(BaseModel):
    note: str

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

class DashboardStats(BaseModel):
    pending_receive: int
    my_pending_confirm: int
    total_this_month: int
    confirmed_this_month: int