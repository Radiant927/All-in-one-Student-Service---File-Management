from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class Campus(str, enum.Enum):
    NANHAI = "nanhai"
    SHIPAI = "shipai"

class TransferStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    OVERDUE = "overdue"
    EXCEPTION = "exception"
    CANCELLED = "cancelled"

class FileType(str, enum.Enum):
    ADMIN = "admin"
    TEACHING = "teaching"
    STUDENT = "student"
    FINANCE = "finance"
    OTHER = "other"

class Urgency(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    campus = Column(SQLEnum(Campus), nullable=False)
    phone = Column(String(20), default="")
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True, index=True)
    transfer_no = Column(String(32), unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    courier_name = Column(String(50), nullable=False)
    courier_phone = Column(String(20), default="")
    receiver_name = Column(String(50), nullable=False)
    receiver_phone = Column(String(20), default="")
    depart_time = Column(DateTime, nullable=False)
    estimate_arrive_time = Column(DateTime)
    confirm_time = Column(DateTime)
    from_campus = Column(SQLEnum(Campus), nullable=False)
    to_campus = Column(SQLEnum(Campus), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False, default=FileType.OTHER)
    urgency = Column(SQLEnum(Urgency), nullable=False, default=Urgency.NORMAL)
    status = Column(SQLEnum(TransferStatus), nullable=False, default=TransferStatus.PENDING)
    confirm_message = Column(Text, default="")
    confirm_by = Column(Integer, ForeignKey("users.id"))
    exception_note = Column(Text, default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    files = relationship("TransferFile", back_populates="transfer", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

class TransferFile(Base):
    __tablename__ = "transfer_files"
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="")
    uploaded_at = Column(DateTime, default=datetime.now)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    transfer = relationship("Transfer", back_populates="files")
    uploader = relationship("User")

class BusSchedule(Base):
    __tablename__ = "bus_schedules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    from_campus = Column(SQLEnum(Campus), nullable=False)
    to_campus = Column(SQLEnum(Campus), nullable=False)
    depart_time = Column(String(10), nullable=False)
    arrive_time = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

class OperationLog(Base):
    __tablename__ = "operation_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), default="")
    target_id = Column(Integer, default=0)
    detail = Column(Text, default="")
    ip_address = Column(String(50), default="")
    created_at = Column(DateTime, default=datetime.now)