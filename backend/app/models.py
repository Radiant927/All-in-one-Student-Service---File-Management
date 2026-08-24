from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Enum as SQLEnum, Float
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


# ---------- 枚举定义 ----------

class Campus(str, enum.Enum):
    """校区枚举：南海 / 石牌"""
    NANHAI = "nanhai"
    SHIPAI = "shipai"


class TransferStatus(str, enum.Enum):
    """转交单状态"""
    PENDING = "pending"        # 待接收（运输中）
    CONFIRMED = "confirmed"    # 已确认收到
    OVERDUE = "overdue"        # 已逾期未确认
    EXCEPTION = "exception"    # 有异常
    CANCELLED = "cancelled"    # 已撤回


class FileType(str, enum.Enum):
    """文件类型"""
    ADMIN = "admin"           # 行政文件
    TEACHING = "teaching"     # 教学资料
    STUDENT = "student"       # 学生材料
    FINANCE = "finance"       # 财务票据
    OTHER = "other"           # 其他


class Urgency(str, enum.Enum):
    """紧急程度"""
    NORMAL = "normal"         # 普通
    URGENT = "urgent"         # 加急
    CRITICAL = "critical"     # 特急


# ---------- 表模型 ----------

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)           # 真实姓名
    campus = Column(SQLEnum(Campus), nullable=False)         # 所属校区
    phone = Column(String(20), default="")                   # 联系电话
    is_admin = Column(Boolean, default=False)                # 是否管理员
    is_active = Column(Boolean, default=True)                # 是否启用
    created_at = Column(DateTime, default=datetime.utcnow)


class Transfer(Base):
    """转交单表（核心业务表）"""
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_no = Column(String(32), unique=True, index=True)  # 系统自动编号
    title = Column(String(200), nullable=False)                # 文件标题/事由
    description = Column(Text, default="")                     # 文件说明/备注

    # 转交相关
    courier_name = Column(String(50), nullable=False)          # 转交同学姓名
    courier_phone = Column(String(20), default="")             # 转交同学电话
    receiver_name = Column(String(50), nullable=False)         # 接收人姓名
    receiver_phone = Column(String(20), default="")            # 接收人电话

    # 时间相关
    depart_time = Column(DateTime, nullable=False)             # 校车出发时间
    estimate_arrive_time = Column(DateTime)                    # 预计到达时间
    confirm_time = Column(DateTime)                            # 实际确认时间

    # 校区方向
    from_campus = Column(SQLEnum(Campus), nullable=False)      # 出发校区
    to_campus = Column(SQLEnum(Campus), nullable=False)        # 目的校区

    # 分类
    file_type = Column(SQLEnum(FileType), nullable=False, default=FileType.OTHER)
    urgency = Column(SQLEnum(Urgency), nullable=False, default=Urgency.NORMAL)

    # 状态
    status = Column(SQLEnum(TransferStatus), nullable=False, default=TransferStatus.PENDING)

    # 确认相关
    confirm_message = Column(Text, default="")                 # 收件留言
    confirm_by = Column(Integer, ForeignKey("users.id"))       # 确认人ID
    exception_note = Column(Text, default="")                  # 异常说明

    # 发起人
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    files = relationship("TransferFile", back_populates="transfer", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class TransferFile(Base):
    """转交附件表（一单对多文件）"""
    __tablename__ = "transfer_files"

    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    original_name = Column(String(255), nullable=False)        # 原始文件名
    stored_name = Column(String(255), nullable=False)          # 存储后的文件名（防止重名）
    file_path = Column(String(500), nullable=False)            # 存储路径
    file_size = Column(Integer, default=0)                     # 文件大小（字节）
    mime_type = Column(String(100), default="")                # MIME 类型
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    transfer = relationship("Transfer", back_populates="files")


class BusSchedule(Base):
    """校车班次表"""
    __tablename__ = "bus_schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)                 # 班次名称，如"上午第一班"
    from_campus = Column(SQLEnum(Campus), nullable=False)      # 出发校区
    to_campus = Column(SQLEnum(Campus), nullable=False)        # 到达校区
    depart_time = Column(String(10), nullable=False)           # 发车时间，如 "08:00"
    arrive_time = Column(String(10), nullable=False)           # 预计到达时间，如 "09:30"
    is_active = Column(Boolean, default=True)                  # 是否启用
    sort_order = Column(Integer, default=0)                    # 排序
    created_at = Column(DateTime, default=datetime.utcnow)


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))          # 操作人
    action = Column(String(50), nullable=False)                # 操作类型：create/confirm/cancel...
    target_type = Column(String(50), default="")               # 操作对象类型：transfer/file/user...
    target_id = Column(Integer, default=0)                     # 操作对象ID
    detail = Column(Text, default="")                          # 操作详情
    ip_address = Column(String(50), default="")                # 操作IP
    created_at = Column(DateTime, default=datetime.utcnow)
