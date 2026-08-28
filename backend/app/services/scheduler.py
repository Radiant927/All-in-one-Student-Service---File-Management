"""定时任务调度器"""
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.config import settings
from app.database import SessionLocal
from app.models import Transfer, TransferStatus
from app.services import notification

logger = logging.getLogger(__name__)

def check_overdue_transfers():
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        overdue_threshold = now - timedelta(hours=settings.OVERDUE_HOURS)
        overdue_list = (
            db.query(Transfer)
            .filter(
                Transfer.status == TransferStatus.PENDING,
                or_(
                    and_(
                        Transfer.estimate_arrive_time.isnot(None),
                        Transfer.estimate_arrive_time < overdue_threshold,
                    ),
                    and_(
                        Transfer.estimate_arrive_time.is_(None),
                        Transfer.depart_time.isnot(None),
                        Transfer.depart_time < overdue_threshold,
                    ),
                ),
            )
            .all()
        )
        if not overdue_list:
            return
        for transfer in overdue_list:
            transfer.status = TransferStatus.OVERDUE
            transfer.updated_at = now
            notification.notify_overdue(transfer)
            logger.info(f"转交单 {transfer.transfer_no} 已逾期，已发送提醒")
        db.commit()
        logger.info(f"本次扫描发现 {len(overdue_list)} 个逾期转交单")
    except Exception as e:
        logger.error(f"逾期检查任务出错：{e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        check_overdue_transfers,
        "interval",
        minutes=30,
        id="check_overdue",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("定时任务调度器已启动")
    return scheduler