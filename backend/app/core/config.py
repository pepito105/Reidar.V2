from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    BRAVE_API_KEY: str
    SENDGRID_API_KEY: str
    CLERK_SECRET_KEY: str
    NOTIFICATION_EMAIL: str
    FROM_EMAIL: str
    APP_URL: str


settings = Settings()
