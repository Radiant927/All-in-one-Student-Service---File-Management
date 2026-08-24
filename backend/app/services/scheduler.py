"""定时任务调度器

用 APScheduler 实现后台定时任务：
- 每 30 分钟扫描一次逾期转交单，自动更新状态并发送提醒
"""
from datetime import datetime, timedelta
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Transfer, TransferStatus
from app.services import notification


logger = logging.getLogger(__name__)


def check_overdue_transfers():
    """检查逾期转交单

    规则：当前时间 > 预计到达时间 + OVERDUE_HOURS，且状态还是 pending 的，
    自动标记为 overdue 并发送微信提醒。
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        overdue_threshold = now - timedelta(hours=settings.OVERDUE_HOURS)

        # 找出逾期的：预计到达时间 < 阈值，且状态是 pending
        overdue_list = (
            db.query(Transfer)
            .filter(
                Transfer.status == TransferStatus.PENDING,
                Transfer.estimate_arrive_time.isnot(None),
                Transfer.estimate_arrive_time < overdue_threshold,
            )
            .all()
        )

        if not overdue_list:
            return

        for transfer in overdue_list:
            transfer.status = TransferStatus.OVERDUE
            transfer.updated_at = now
            # 发送逾期提醒
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
    """启动定时任务调度器（在应用启动时调用）"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    # 每 30 分钟执行一次逾期检查
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
