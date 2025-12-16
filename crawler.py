#!/usr/bin/env python3
"""
Simple crawler wrapper that uses smart_archiver_v2.py
For GitHub Actions and AI automation.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main crawler entry point."""
    try:
        # Import archiver (in same directory)
        from smart_archiver_v2 import WARCCompliantArchiver
        
        # Get config from environment
        start_url = os.getenv('START_URL', 'https://example.com')
        max_pages = int(os.getenv('MAX_PAGES', '50'))
        db_file = os.getenv('DB_FILE', 'archive.db')
        
        logger.info(f"Starting crawl: {start_url}")
        logger.info(f"Max pages: {max_pages}")
        logger.info(f"Database: {db_file}")
        
        # Create archiver
        archiver = WARCCompliantArchiver(
            start_url=start_url,
            db_path=db_file,
            max_depth=5,
            max_pages=max_pages
        )
        
        # Run crawl
        await archiver.archive()
        
        logger.info("\n" + "="*50)
        logger.info(f"✅ Crawl complete!")
        logger.info(f"Database saved: {db_file}")
        logger.info("="*50)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
