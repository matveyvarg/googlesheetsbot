from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Server(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    client_id: str
    client_secret: str
    service_account_file: str
    sheet_name: str
    transactions_column: int = 7
    income_column: int = 1
    bot_token: str
    user_id: str
    redis_dsn: str
    keyboard_key: str = "keyboard"
    server: Server = Field(default_factory=Server)  # type: ignore[arg-type]
    secret_token: str
    webhook_path: str = "/webhook"
    base_webhook_url: str
    loglevel: str = "INFO"
    model_config = SettingsConfigDict(env_nested_delimiter="__")


settings = Settings()
