import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, TransferFile, Transfer
from app.auth import get_current_user

router = APIRouter(prefix="/api/files", tags=["文件管理"])

def _get_upload_dir() -> str:
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def _save_file(file: UploadFile) -> dict:
    upload_dir = _get_upload_dir()
    original_name = file.filename or "unknown"
    _, ext = os.path.splitext(original_name)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)
    file_size = 0
    with open(file_path, "wb") as f:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > settings.MAX_UPLOAD_SIZE:
                f.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件大小超过限制，最大允许 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB",
                )
            f.write(chunk)
    return {
        "original_name": original_name,
        "stored_name": stored_name,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": file.content_type or "",
    }

@router.post("/upload", summary="上传文件（支持多文件）")
def upload_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = []
    for file in files:
        file_info = _save_file(file)
        db_file = TransferFile(
            transfer_id=0,
            uploaded_by=current_user.id,
            original_name=file_info["original_name"],
            stored_name=file_info["stored_name"],
            file_path=file_info["file_path"],
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        result.append({
            "id": db_file.id,
            "original_name": db_file.original_name,
            "file_size": db_file.file_size,
            "mime_type": db_file.mime_type,
            "uploaded_at": db_file.uploaded_at,
        })
    return result

@router.get("/{file_id}/download", summary="下载文件")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = db.query(TransferFile).filter(TransferFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    if db_file.transfer_id and db_file.transfer_id != 0:
        transfer = db.query(Transfer).filter(Transfer.id == db_file.transfer_id).first()
        if not transfer:
            raise HTTPException(status_code=404, detail="关联转交单不存在")
        is_allowed = (
            transfer.created_by == current_user.id
            or transfer.to_campus == current_user.campus
            or transfer.from_campus == current_user.campus
            or current_user.is_admin
        )
        if not is_allowed:
            raise HTTPException(status_code=403, detail="无权下载此文件")
    else:
        if db_file.uploaded_by != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="无权下载此文件")
    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_name,
        media_type=db_file.mime_type or "application/octet-stream",
    )

@router.delete("/{file_id}", summary="删除文件")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = db.query(TransferFile).filter(TransferFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    if db_file.transfer_id and db_file.transfer_id != 0:
        raise HTTPException(status_code=400, detail="已关联到转交单的文件不能单独删除")
    if db_file.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权删除此文件")
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)
    db.delete(db_file)
    db.commit()
    return {"message": "文件已删除"}