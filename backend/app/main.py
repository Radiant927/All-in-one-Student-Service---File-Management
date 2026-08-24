from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth as auth_router
from app.routers import files as files_router
from app.routers import transfers as transfers_router
from app.routers import buses as buses_router
from app.routers import notification as notification_router
from app.routers import stats as stats_router


scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时开定时任务，关闭时停掉"""
    global scheduler
    from app.services.scheduler import start_scheduler
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    description="佛山南海校区 ↔ 广州石牌校区 文件转交追踪与确认平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 跨域配置：前后端分离时，前端从不同端口来访问后端，需要允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段全开，生产环境建议限定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """根路径，健康检查用"""
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "env": settings.APP_ENV,
    }


@app.get("/hello")
def hello(name: str = "同学"):
    """示例接口：打个招呼

    访问 http://localhost:8000/hello?name=小明 试试
    """
    return {"message": f"你好，{name}！欢迎使用跨校区文件交接管理系统"}


# ---------- 注册路由 ----------
app.include_router(auth_router.router)
app.include_router(files_router.router)
app.include_router(transfers_router.router)
app.include_router(buses_router.router)
app.include_router(notification_router.router)
app.include_router(stats_router.router)
