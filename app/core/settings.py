from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FaxCloud Analyzer"
    env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    use_postgres: bool = False
    database_url: str = "sqlite+aiosqlite:///./data/faxcloud.db"
    postgres_url: str = "postgresql+psycopg://user:password@localhost:5432/faxcloud"
    admin_user: str = "admin"
    admin_pass: str = "change-me"
    allow_duplicates: bool = False
    public_qr_allowed: bool = True
    watch_inbox: bool = False
    inbox_path: Path = Path("./data/inbox")
    log_level: str = "INFO"
    uploads_dir: Path = Path("./data/uploads")
    qrcodes_dir: Path = Path("./data/qrcodes")
    logs_dir: Path = Path("./data/logs")
    columns_config: Path = Path("./config/columns.yaml")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def resolved_database_url(self) -> str:
        if self.use_postgres:
            return self.postgres_url
        return self.database_url


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.qrcodes_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)
settings.inbox_path.mkdir(parents=True, exist_ok=True)
