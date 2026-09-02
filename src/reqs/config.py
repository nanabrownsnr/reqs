import os

import logging
from logging.handlers import TimedRotatingFileHandler

from pydantic_settings import BaseSettings, SettingsConfigDict

mcp_name = "requirements_gathering"


def configure_logging():
    os.makedirs("./logs", exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        filename=f"./logs/{mcp_name}_mcp.log",
        when="midnight",
        interval=1,
        backupCount=7,
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    detailed_handler = TimedRotatingFileHandler(
        filename=f"./logs/{mcp_name}_mcp_detailed.log",
        when="midnight",
        interval=1,
        backupCount=7,
    )
    detailed_handler.setFormatter(formatter)
    detailed_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(detailed_handler)


class Settings(BaseSettings):
    database_url: str
    openrouter_url: str
    openrouter_model: str
    public_url: str

    service_id: str = f"{mcp_name}_mcp"
    app_title: str = f"{mcp_name.title()} MCP"
    app_version: str = "1.0.0"
    enviroment: str
    api_v1_str: str = "/api/v1"
    allowed_origins: str = "*"
    release_id: str = "1.0.0"
    persona_id_header: str = "Persona-Id"

    usage_report_endpoint: str

    account_service_url: str
    account_service_jwks_cache_ttl: int
    account_service_jwks_endpoint: str

    license_key: str
    license_server_base_url: str
    license_server_jwks_endpoint: str
    license_server_activation_endpoint: str

    environment: str = "development"
    encryption_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
configure_logging()
