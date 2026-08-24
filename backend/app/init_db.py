"""数据库初始化脚本：建表 + 插入初始数据

首次部署时运行：  python -m app.init_db
"""
from datetime import datetime

from passlib.context import CryptContext

from app.database import Base, engine, SessionLocal
from app.models import User, Campus, BusSchedule, FileType, Urgency


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_database():
    # 1. 创建所有表（如果表已存在不会重复创建）
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据表创建完成")

    db = SessionLocal()

    try:
        # 2. 初始化用户
        if db.query(User).count() == 0:
            users = [
                User(
                    username="nanhai",
                    hashed_password=pwd_context.hash("admin123"),
                    real_name="南海校区负责人",
                    campus=Campus.NANHAI,
                    phone="",
                    is_admin=True,
                ),
                User(
                    username="shipai",
                    hashed_password=pwd_context.hash("admin123"),
                    real_name="石牌校区负责人",
                    campus=Campus.SHIPAI,
                    phone="",
                    is_admin=True,
                ),
            ]
            db.add_all(users)
            db.commit()
            print("[OK] 初始用户创建完成（nanhai / shipai，密码 admin123）")
        else:
            print("[INFO] 用户已存在，跳过初始化")

        # 3. 初始化校车班次（示例数据）
        if db.query(BusSchedule).count() == 0:
            schedules = [
                # 南海 → 石牌
                BusSchedule(name="上午第一班", from_campus=Campus.NANHAI, to_campus=Campus.SHIPAI,
                            depart_time="07:30", arrive_time="09:00", sort_order=1),
                BusSchedule(name="上午第二班", from_campus=Campus.NANHAI, to_campus=Campus.SHIPAI,
                            depart_time="10:00", arrive_time="11:30", sort_order=2),
                BusSchedule(name="下午第一班", from_campus=Campus.NANHAI, to_campus=Campus.SHIPAI,
                            depart_time="14:00", arrive_time="15:30", sort_order=3),
                BusSchedule(name="下午第二班", from_campus=Campus.NANHAI, to_campus=Campus.SHIPAI,
                            depart_time="16:30", arrive_time="18:00", sort_order=4),
                # 石牌 → 南海
                BusSchedule(name="上午第一班", from_campus=Campus.SHIPAI, to_campus=Campus.NANHAI,
                            depart_time="08:00", arrive_time="09:30", sort_order=1),
                BusSchedule(name="上午第二班", from_campus=Campus.SHIPAI, to_campus=Campus.NANHAI,
                            depart_time="10:30", arrive_time="12:00", sort_order=2),
                BusSchedule(name="下午第一班", from_campus=Campus.SHIPAI, to_campus=Campus.NANHAI,
                            depart_time="14:30", arrive_time="16:00", sort_order=3),
                BusSchedule(name="下午第二班", from_campus=Campus.SHIPAI, to_campus=Campus.NANHAI,
                            depart_time="17:00", arrive_time="18:30", sort_order=4),
            ]
            db.add_all(schedules)
            db.commit()
            print("[OK] 校车班次初始化完成（8 条示例数据）")
        else:
            print("[INFO] 校车班次已存在，跳过初始化")

    finally:
        db.close()

    print("\n[DONE] 数据库初始化完成！")


if __name__ == "__main__":
    init_database()
