"""Environment-based application settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Settings loaded from process environment and backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Vyanic Stockist Management Portal"
    app_env: str = "development"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "vyanic_stockist"
    mysql_user: str = ""
    mysql_password: SecretStr = SecretStr("")

    mongodb_uri: SecretStr = SecretStr("mongodb://127.0.0.1:27017")
    mongodb_database: str = "vyanic_stockist"

    jwt_secret: SecretStr = SecretStr("")
    jwt_access_token_minutes: int = Field(default=30, gt=0, le=1440)

    @property
    def sqlalchemy_url(self) -> URL:
        """Build a safely escaped MySQL URL from environment configuration."""
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user or None,
            password=self.mysql_password.get_secret_value() or None,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
