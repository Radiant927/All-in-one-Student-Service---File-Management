from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置，从 .env 文件自动读取"""

    # 应用基本信息
    APP_NAME: str = "跨校区文件交接管理系统"
    APP_ENV: str = "dev"

    # 数据库
    DATABASE_URL: str = "sqlite:///./campus_file.db"

    # JWT 鉴权
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # 企业微信机器人
    WECHAT_WEBHOOK_URL: str = ""

    # 逾期提醒（小时）
    OVERDUE_HOURS: int = 3

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
