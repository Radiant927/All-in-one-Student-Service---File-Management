from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Transfer, TransferStatus, FileType, Urgency
from app.schemas import TransferCreate, TransferUpdate, TransferResponse, TransferListResponse, ConfirmTransfer, ReportException
from app.auth import get_current_user
from app.services import transfer_service

router = APIRouter(prefix="/api/transfers", tags=["转交单管理"])

@router.post("", response_model=TransferResponse, summary="发起转交单")
def create_transfer(
    form: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if form.to_campus == current_user.campus:
        raise HTTPException(status_code=400, detail="不能发给同一校区")
    try:
        transfer = transfer_service.create_transfer(
            db=db, data=form.model_dump(exclude={"file_ids"}),
            file_ids=form.file_ids, creator=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transfer

@router.get("", response_model=TransferListResponse, summary="获取转交单列表")
def list_transfers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TransferStatus] = None,
    file_type: Optional[FileType] = None,
    urgency: Optional[Urgency] = None,
    role: Optional[str] = Query(None, description="sent=我发起的, received=发给我的"),
    keyword: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if role and role not in ("sent", "received"):
        raise HTTPException(status_code=400, detail="role 参数只能是 sent 或 received")
    items, total = transfer_service.get_transfer_list(
        db=db, user=current_user, page=page, page_size=page_size,
        status=status, file_type=file_type, urgency=urgency,
        role=role, keyword=keyword, date_from=date_from, date_to=date_to,
    )
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.get("/{transfer_id}", response_model=TransferResponse, summary="获取转交单详情")
def get_transfer_detail(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转交单不存在")
    is_related = (
        transfer.created_by == current_user.id
        or transfer.to_campus == current_user.campus
        or transfer.from_campus == current_user.campus
        or current_user.is_admin
    )
    if not is_related:
        raise HTTPException(status_code=403, detail="无权查看此转交单")
    return transfer

@router.put("/{transfer_id}", response_model=TransferResponse, summary="编辑转交单")
def update_transfer(
    transfer_id: int,
    form: TransferUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转交单不存在")
    try:
        transfer = transfer_service.update_transfer(
            db=db, transfer=transfer,
            data=form.model_dump(exclude_unset=True), operator=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transfer

@router.post("/{transfer_id}/cancel", response_model=TransferResponse, summary="撤回转交单")
def cancel_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转交单不存在")
    try:
        transfer = transfer_service.cancel_transfer(db, transfer, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transfer

@router.post("/{transfer_id}/confirm", response_model=TransferResponse, summary="确认收到")
def confirm_transfer(
    transfer_id: int,
    form: ConfirmTransfer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转交单不存在")
    try:
        transfer = transfer_service.confirm_transfer(
            db, transfer, current_user, form.message, form.file_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transfer

@router.post("/{transfer_id}/exception", response_model=TransferResponse, summary="上报异常")
def report_exception(
    transfer_id: int,
    form: ReportException,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转交单不存在")
    try:
        transfer = transfer_service.report_exception(db, transfer, current_user, form.note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transfer