from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models import Transfer, TransferFile, User, Campus, TransferStatus, FileType, Urgency, OperationLog
from app.services import notification

def generate_transfer_no(from_campus: Campus, to_campus: Campus, db: Session) -> str:
    from_code = "NH" if from_campus == Campus.NANHAI else "SP"
    to_code = "NH" if to_campus == Campus.NANHAI else "SP"
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"{from_code}-{to_code}-{today_str}-"
    last = (
        db.query(Transfer)
        .filter(Transfer.transfer_no.like(f"{prefix}%"))
        .order_by(Transfer.id.desc())
        .first()
    )
    if last:
        last_seq = int(last.transfer_no.split("-")[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    return f"{prefix}{new_seq:03d}"

def create_transfer(db: Session, data: dict, file_ids: List[int], creator: User) -> Transfer:
    from_campus = creator.campus
    transfer_no = generate_transfer_no(from_campus, data["to_campus"], db)
    transfer = Transfer(
        transfer_no=transfer_no,
        title=data["title"],
        description=data.get("description", ""),
        courier_name=data["courier_name"],
        courier_phone=data.get("courier_phone", ""),
        receiver_name=data["receiver_name"],
        receiver_phone=data.get("receiver_phone", ""),
        depart_time=data["depart_time"],
        estimate_arrive_time=data.get("estimate_arrive_time"),
        from_campus=from_campus,
        to_campus=data["to_campus"],
        file_type=data.get("file_type", FileType.OTHER),
        urgency=data.get("urgency", Urgency.NORMAL),
        status=TransferStatus.PENDING,
        created_by=creator.id,
    )
    db.add(transfer)
    db.flush()
    if file_ids:
        db.query(TransferFile).filter(
            TransferFile.id.in_(file_ids),
            TransferFile.transfer_id == 0,
        ).update({TransferFile.transfer_id: transfer.id}, synchronize_session=False)
    _log_operation(db, creator.id, "create", "transfer", transfer.id, f"发起转交单 {transfer_no}")
    db.commit()
    db.refresh(transfer)
    notification.notify_new_transfer(transfer)
    return transfer

def update_transfer(db: Session, transfer: Transfer, data: dict, operator: User) -> Transfer:
    if transfer.status != TransferStatus.PENDING:
        raise ValueError("只有待接收状态的转交单可以编辑")
    if transfer.created_by != operator.id:
        raise ValueError("只能编辑自己发起的转交单")
    for key, value in data.items():
        if value is not None and hasattr(transfer, key) and key != "file_ids":
            setattr(transfer, key, value)
    if "file_ids" in data and data["file_ids"] is not None:
        db.query(TransferFile).filter(
            TransferFile.transfer_id == transfer.id
        ).update({TransferFile.transfer_id: 0}, synchronize_session=False)
        if data["file_ids"]:
            db.query(TransferFile).filter(
                TransferFile.id.in_(data["file_ids"]),
                TransferFile.transfer_id == 0,
            ).update({TransferFile.transfer_id: transfer.id}, synchronize_session=False)
    _log_operation(db, operator.id, "update", "transfer", transfer.id, f"编辑转交单 {transfer.transfer_no}")
    transfer.updated_at = datetime.now()
    db.commit()
    db.refresh(transfer)
    return transfer

def cancel_transfer(db: Session, transfer: Transfer, operator: User) -> Transfer:
    if transfer.status != TransferStatus.PENDING:
        raise ValueError("只有待接收状态的转交单可以撤回")
    if transfer.created_by != operator.id:
        raise ValueError("只能撤回自己发起的转交单")
    transfer.status = TransferStatus.CANCELLED
    transfer.updated_at = datetime.now()
    _log_operation(db, operator.id, "cancel", "transfer", transfer.id, f"撤回转交单 {transfer.transfer_no}")
    db.commit()
    db.refresh(transfer)
    return transfer

def confirm_transfer(db: Session, transfer: Transfer, operator: User, message: str = "", file_ids: Optional[List[int]] = None) -> Transfer:
    if transfer.status not in (TransferStatus.PENDING, TransferStatus.OVERDUE):
        raise ValueError("当前状态不允许确认")
    if operator.campus != transfer.to_campus:
        raise ValueError("只有接收校区的负责人可以确认收到")
    transfer.status = TransferStatus.CONFIRMED
    transfer.confirm_time = datetime.now()
    transfer.confirm_message = message
    transfer.confirm_by = operator.id
    transfer.updated_at = datetime.now()
    if file_ids:
        db.query(TransferFile).filter(
            TransferFile.id.in_(file_ids),
            TransferFile.transfer_id == 0,
        ).update({TransferFile.transfer_id: transfer.id}, synchronize_session=False)
    _log_operation(db, operator.id, "confirm", "transfer", transfer.id, f"确认收到转交单 {transfer.transfer_no}")
    db.commit()
    db.refresh(transfer)
    notification.notify_transfer_confirmed(transfer)
    return transfer

def report_exception(db: Session, transfer: Transfer, operator: User, note: str) -> Transfer:
    if operator.campus != transfer.to_campus:
        raise ValueError("只有接收校区的负责人可以上报异常")
    transfer.status = TransferStatus.EXCEPTION
    transfer.exception_note = note
    transfer.updated_at = datetime.now()
    _log_operation(db, operator.id, "exception", "transfer", transfer.id, f"转交单 {transfer.transfer_no} 异常：{note}")
    db.commit()
    db.refresh(transfer)
    notification.notify_transfer_exception(transfer)
    return transfer

def get_transfer_list(
    db: Session, user: User, page: int = 1, page_size: int = 20,
    status: Optional[TransferStatus] = None, file_type: Optional[FileType] = None,
    urgency: Optional[Urgency] = None, role: Optional[str] = None,
    keyword: Optional[str] = None, date_from: Optional[date] = None, date_to: Optional[date] = None,
) -> tuple:
    query = db.query(Transfer)
    if role == "sent":
        query = query.filter(Transfer.created_by == user.id)
    elif role == "received":
        query = query.filter(Transfer.to_campus == user.campus)
    if status:
        query = query.filter(Transfer.status == status)
    if file_type:
        query = query.filter(Transfer.file_type == file_type)
    if urgency:
        query = query.filter(Transfer.urgency == urgency)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(or_(
            Transfer.title.like(kw),
            Transfer.courier_name.like(kw),
            Transfer.receiver_name.like(kw),
            Transfer.transfer_no.like(kw),
        ))
    if date_from:
        query = query.filter(Transfer.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Transfer.created_at <= datetime.combine(date_to, datetime.max.time()))
    total = query.count()
    items = (
        query.order_by(Transfer.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total

def _log_operation(db: Session, user_id: int, action: str, target_type: str, target_id: int, detail: str = ""):
    log = OperationLog(
        user_id=user_id, action=action, target_type=target_type,
        target_id=target_id, detail=detail,
    )
    db.add(log)