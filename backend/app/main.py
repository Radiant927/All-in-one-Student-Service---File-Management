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
from app.routers import logs as logs_router
from app.routers import users as users_router

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running", "env": settings.APP_ENV}

@app.get("/hello")
def hello(name: str = "同学"):
    return {"message": f"你好，{name}！欢迎使用跨校区文件交接管理系统"}

app.include_router(auth_router.router)
app.include_router(files_router.router)
app.include_router(transfers_router.router)
app.include_router(buses_router.router)
app.include_router(notification_router.router)
app.include_router(stats_router.router)
app.include_router(logs_router.router)
app.include_router(users_router.router)