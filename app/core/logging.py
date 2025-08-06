import logging
import logging.handlers
import os
import glob
from datetime import datetime, timedelta
from app.core.config import settings

def cleanup_old_logs():
    """Clean up old log files to prevent disk space issues."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return
    
    # Delete old log files (configurable cleanup period)
    cutoff_date = datetime.now() - timedelta(days=settings.log_cleanup_days)
    
    # Find all log files
    log_patterns = [
        os.path.join(log_dir, "api_*.log*"),
        os.path.join(log_dir, "*.log.*"),
    ]
    
    cleaned_count = 0
    for pattern in log_patterns:
        for log_file in glob.glob(pattern):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_date:
                    os.remove(log_file)
                    cleaned_count += 1
                    print(f"🗑️ Removed old log file: {log_file}")
            except Exception as e:
                print(f"❌ Could not remove log file {log_file}: {e}")
    
    if cleaned_count > 0:
        print(f"✅ Cleaned up {cleaned_count} old log files")
    else:
        print("ℹ️ No old log files to clean up")

def setup_logging():
    """Setup logging configuration with rotation to prevent disk space issues."""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Clean up old logs first
    cleanup_old_logs()
    
    # Configure logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create rotating file handler with configurable disk management
    log_file = os.path.join(log_dir, "azure_test_import.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=settings.log_max_file_size_mb * 1024 * 1024,  # Configurable file size
        backupCount=settings.log_backup_count,  # Configurable backup count
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to avoid too verbose output
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    total_max_size = settings.log_max_file_size_mb * (settings.log_backup_count + 1)
    logging.info(f"📝 Logging setup completed: {settings.log_max_file_size_mb}MB per file, "
                f"{settings.log_backup_count} backups, max total: {total_max_size}MB, "
                f"cleanup after {settings.log_cleanup_days} days")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

def get_latest_log_file() -> str:
    """Get the path to the latest log file."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return None
    
    # Look for log files
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not log_files:
        return None
    
    # Sort by modification time and get the latest
    log_files.sort(key=lambda f: os.path.getmtime(os.path.join(log_dir, f)), reverse=True)
    return os.path.join(log_dir, log_files[0])