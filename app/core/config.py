import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Azure DevOps Configuration (Server URL only)
    azure_devops_org_url: str = os.getenv("AZURE_DEVOPS_ORG_URL", "http://192.168.10.22:8080/tfs/RPKavoshDevOps")
    azure_devops_api_version: str = "5.0"
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Azure DevOps Test Plan Import API"
    version: str = "1.0.0"
    description: str = "API for importing Gherkin features to Azure DevOps Test Plans"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_max_file_size_mb: int = int(os.getenv("LOG_MAX_FILE_SIZE_MB", "5"))
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))
    log_cleanup_days: int = int(os.getenv("LOG_CLEANUP_DAYS", "7"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


settings = Settings() 