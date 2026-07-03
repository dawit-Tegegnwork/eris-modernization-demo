from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "eRIS Modernization Demo"
    api_prefix: str = "/api/v1"
    secret_key: str = "portfolio-demo-secret-change-in-production"
    database_url: str = "sqlite:///./eris_demo.db"
    token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_prefix="ERIS_", env_file=".env")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
