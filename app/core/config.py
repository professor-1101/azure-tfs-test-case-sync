import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Azure DevOps Configuration
    azure_devops_org_url: str = os.getenv("AZURE_DEVOPS_ORG_URL", "http://192.168.10.22:8080/tfs/RPKavoshDevOps")
    azure_devops_project: str = os.getenv("AZURE_DEVOPS_PROJECT", "Test Process")
    azure_devops_api_version: str = "5.0"
    
    # Test Plan Configuration
    azure_devops_test_plan: str = os.getenv("AZURE_DEVOPS_TEST_PLAN", "تست کارتال")
    azure_devops_test_suite: str = os.getenv("AZURE_DEVOPS_TEST_SUITE", "غیر فعال ‌سازی")
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Azure DevOps Test Plan Import API"
    version: str = "1.0.0"
    description: str = "API for importing Gherkin features to Azure DevOps Test Plans"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_max_file_size_mb: int = int(os.getenv("LOG_MAX_FILE_SIZE_MB", "5"))  # 5MB default
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))  # 3 backup files
    log_cleanup_days: int = int(os.getenv("LOG_CLEANUP_DAYS", "7"))  # Keep logs for 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 