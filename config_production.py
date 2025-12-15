#!/usr/bin/env python3
"""
Production configuration for web crawler.
Loads settings from .env file and validates them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Load .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    load_dotenv(env_file)


class Config:
    """Production configuration"""
    
    # Core crawler settings
    START_URL = os.getenv('START_URL', 'https://example.com')
    MAX_PAGES = int(os.getenv('MAX_PAGES', 50))
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', 30))
    
    # Rate limiting (requests per second)
    RATE_LIMIT_PER_SEC = float(os.getenv('RATE_LIMIT_PER_SEC', 2.0))
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_BACKOFF_FACTOR = float(os.getenv('RETRY_BACKOFF_FACTOR', 2.0))
    
    # Database
    DB_FILE = os.getenv('DB_FILE', 'crawler.db')
    USE_DB = os.getenv('USE_DB', 'true').lower() == 'true'
    ENABLE_DB = os.getenv('ENABLE_DB', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'crawler.log')
    
    # Connection pool
    CONN_LIMIT_PER_HOST = int(os.getenv('CONN_LIMIT_PER_HOST', 2))
    CONN_LIMIT_TOTAL = int(os.getenv('CONN_LIMIT_TOTAL', 10))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Validate START_URL
        try:
            parsed = urlparse(cls.START_URL)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"Invalid START_URL: {cls.START_URL}")
        except Exception as e:
            errors.append(f"Error parsing START_URL: {e}")
        
        # Validate numbers
        if cls.MAX_PAGES <= 0:
            errors.append("MAX_PAGES must be > 0")
        
        if cls.TIMEOUT_SECONDS <= 0:
            errors.append("TIMEOUT_SECONDS must be > 0")
        
        if cls.RATE_LIMIT_PER_SEC <= 0:
            errors.append("RATE_LIMIT_PER_SEC must be > 0")
        
        if cls.MAX_RETRIES < 0:
            errors.append("MAX_RETRIES must be >= 0")
        
        if cls.RETRY_BACKOFF_FACTOR < 1:
            errors.append("RETRY_BACKOFF_FACTOR must be >= 1")
        
        if cls.CONN_LIMIT_PER_HOST <= 0:
            errors.append("CONN_LIMIT_PER_HOST must be > 0")
        
        if cls.CONN_LIMIT_TOTAL <= 0:
            errors.append("CONN_LIMIT_TOTAL must be > 0")
        
        if errors:
            for error in errors:
                logger.error(f"Config error: {error}")
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        logger.info("✅ Configuration valid")
        return True
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary"""
        return {
            'start_url': cls.START_URL,
            'max_pages': cls.MAX_PAGES,
            'timeout_seconds': cls.TIMEOUT_SECONDS,
            'rate_limit_per_sec': cls.RATE_LIMIT_PER_SEC,
            'max_retries': cls.MAX_RETRIES,
            'retry_backoff_factor': cls.RETRY_BACKOFF_FACTOR,
            'db_enabled': cls.USE_DB or cls.ENABLE_DB,
            'db_file': cls.DB_FILE,
            'log_level': cls.LOG_LEVEL,
            'log_file': cls.LOG_FILE,
            'conn_limit_per_host': cls.CONN_LIMIT_PER_HOST,
            'conn_limit_total': cls.CONN_LIMIT_TOTAL,
        }


if __name__ == '__main__':
    # Test configuration
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        Config.validate()
        summary = Config.get_summary()
        print("\n🔐 Current Configuration:")
        print(json.dumps(summary, indent=2))
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}")
        exit(1)
