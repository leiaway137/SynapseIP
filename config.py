"""
SynapseIP Configuration & Settings
"""
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import sys

# Load environment variables
load_dotenv(override=True)

# ============================================================
# Application Settings
# ============================================================
class Settings:
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "synapseip_local_dev_secret_key_fixed_123")
    ALGORITHM = "HS256"
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATA_DIR = os.environ.get("DATA_DIR", ".")
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://192.168.1.174:8002")
    DEV_ALLOW_ALL_ORIGINS = os.getenv("DEV_ALLOW_ALL_ORIGINS") == "true"
    
    # Rate Limiting Configuration
    RATE_LIMIT_AUTH_REQUESTS = 5
    RATE_LIMIT_AUTH_WINDOW = 60
    RATE_LIMIT_DEFAULT_REQUESTS = 100
    RATE_LIMIT_DEFAULT_WINDOW = 60
    RATE_LIMIT_AI_GENERATION_REQUESTS = 10
    RATE_LIMIT_AI_GENERATION_WINDOW = 3600
    RATE_LIMIT_ADMIN_REQUESTS = 50
    RATE_LIMIT_ADMIN_WINDOW = 60
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_OPS_LIMIT = int(os.getenv("CIRCUIT_BREAKER_OPS_LIMIT", 500))
    CIRCUIT_BREAKER_TOKEN_LIMIT = int(os.getenv("CIRCUIT_BREAKER_TOKEN_LIMIT", 1000000))
    
    # AI Model Configuration
    LMSTUDIO_API_BASE = os.getenv("LMSTUDIO_API_BASE", "http://127.0.0.1:1234/v1")
    LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "dummy_key")
    LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "qwen3.6-35b-a3b-mlx")
    LMSTUDIO_EMBED_MODEL = os.getenv("LMSTUDIO_EMBED_MODEL", "text-embedding-nomic-embed-text-v1.5")
    
    VLLM_API_BASE = os.getenv("VLLM_API_BASE", "http://192.168.1.151:8000/v1")
    VLLM_API_KEY = os.getenv("VLLM_API_KEY", "dummy_key")
    VLLM_MODEL = os.getenv("VLLM_MODEL", "qwen3.5-122b")
    
    # Input Size Limits
    MAX_TITLE_LENGTH = 200
    MAX_CONTENT_LENGTH = 1000000  # 1MB
    MAX_URL_LENGTH = 500
    MAX_NAME_LENGTH = 100
    MAX_FEEDBACK_LENGTH = 5000
    MAX_CHAT_CONTENT_LENGTH = 50000
    MAX_PASSWORD_LENGTH = 128
    MAX_HOSTNAME_LENGTH = 255

settings = Settings()

# ============================================================
# Logging Setup
# ============================================================
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Root logger
    logger = logging.getLogger('synapseip')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        'logs/synapseip.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/synapseip_errors.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(error_handler)
    
    return logger

# Initialize logger
logger = setup_logging()