from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, BusSchedule, Campus
from app.schemas import BusScheduleCreate, BusScheduleUpdate, BusScheduleResponse
from app.auth import get_current_user


router = APIRouter(prefix="/api/buses", tags=["校车班次"])


@router.get("", response_model=List[BusScheduleResponse], summary="获取校车班次列表")
def list_schedules(
    from_campus: Optional[Campus] = Query(None, description="按出发校区过滤"),
    to_campus: Optional[Campus] = Query(None, description="按到达校区过滤"),
    only_active: bool = Query(True, description="只显示启用的"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取校车班次列表，支持按校区过滤"""
    query = db.query(BusSchedule)

    if from_campus:
        query = query.filter(BusSchedule.from_campus == from_campus)
    if to_campus:
        query = query.filter(BusSchedule.to_campus == to_campus)
    if only_active:
        query = query.filter(BusSchedule.is_active == True)

    # 按出发校区、排序号、发车时间排序
    items = query.order_by(
        BusSchedule.from_campus,
        BusSchedule.sort_order,
        BusSchedule.depart_time,
    ).all()
    return items


@router.get("/{schedule_id}", response_model=BusScheduleResponse, summary="获取班次详情")
def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedule = db.query(BusSchedule).filter(BusSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="班次不存在")
    return schedule


@router.post("", response_model=BusScheduleResponse, summary="新增班次")
def create_schedule(
    form: BusScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增校车班次（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    if form.from_campus == form.to_campus:
        raise HTTPException(status_code=400, detail="出发校区和到达校区不能相同")

    schedule = BusSchedule(**form.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.put("/{schedule_id}", response_model=BusScheduleResponse, summary="编辑班次")
def update_schedule(
    schedule_id: int,
    form: BusScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """编辑校车班次（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    schedule = db.query(BusSchedule).filter(BusSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="班次不存在")

    for key, value in form.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", summary="删除班次")
def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除校车班次（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    schedule = db.query(BusSchedule).filter(BusSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="班次不存在")

    db.delete(schedule)
    db.commit()
    return {"message": "删除成功"}
