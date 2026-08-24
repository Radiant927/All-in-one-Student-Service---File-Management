from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# create_engine：创建数据库引擎，相当于建立和数据库的连接通道
# SQLite 是文件型数据库，不需要安装服务端，一个 .db 文件就是整个数据库
connect_args = {"check_same_thread": False}  # SQLite 专属配置，允许多线程访问
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# SessionLocal：数据库会话工厂，每次要操作数据库时就造一个 session
# session 相当于"一次数据库对话"，用完要关闭
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base：所有数据模型的基类，我们的表模型都要继承它
# 继承了 Base 的类，SQLAlchemy 才知道"这是一张数据库表"
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入用：每个请求自动分配一个 db session，请求结束自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
