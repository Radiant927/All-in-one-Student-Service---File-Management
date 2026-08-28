from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "跨校区文件交接管理系统"
    APP_ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./campus_file.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    WECHAT_WEBHOOK_URL: str = ""
    OVERDUE_HOURS: int = 3
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def cors_origins(self) -> list:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

settings = Settings()