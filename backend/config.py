from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pequeno Rebanho"
    environment: str = "development"
    debug: bool = False
    supabase_url: str = Field(..., min_length=10)
    supabase_key: str = Field(..., min_length=20)
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    allowed_hosts: str = "localhost,127.0.0.1,0.0.0.0"
    rate_limit_per_minute: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"development", "production", "testing"}:
            raise ValueError("environment must be one of: development, production, testing")
        return normalized

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        parts = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not parts:
            raise ValueError("cors_origins must contain at least one valid URL")
        return ",".join(parts)

    @field_validator("allowed_hosts")
    @classmethod
    def validate_allowed_hosts(cls, value: str) -> str:
        hosts = [host.strip() for host in value.split(",") if host.strip()]
        if not hosts:
            raise ValueError("allowed_hosts must contain at least one host")
        return ",".join(hosts)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


settings = Settings()
