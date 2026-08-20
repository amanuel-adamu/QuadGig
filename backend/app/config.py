from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    supabase_url: str
    supabase_service_role_key: str
    stripe_secret_key: str
    stripe_webhook_secret: str


settings = Settings()
