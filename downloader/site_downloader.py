#!/usr/bin/env python3
"""
🚀 ULTIMATE WEBSITE DOWNLOADER

Python module for downloading complete websites with all assets.
Supports multiple backends: httrack, wget, monolith

Модуль для полного скачивания сайтов с всеми ресурсами
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urlparse
import shutil


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SiteDownloader:
    """
    🚀 Ultra-fast website downloader with multiple backends
    
    Usage:
        downloader = SiteDownloader()
        downloader.download('https://example.com', method='httrack')
    """
    
    def __init__(self, download_dir: str = 'downloads'):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.threads = 16
        self.timeout = 30
        
    def _check_tool(self, tool: str) -> bool:
        """Check if tool is installed"""
        return shutil.which(tool) is not None
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    
    def _run_command(self, cmd: List[str], description: str) -> bool:
        """Execute shell command"""
        try:
            logger.info(f"🚀 {description}")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=False
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {description} - Success!")
                return True
            else:
                logger.error(f"❌ {description} - Failed!")
                return False
        except Exception as e:
            logger.error(f"💥 Error: {str(e)}")
            return False
    
    def download_httrack(self, url: str) -> Optional[Path]:
        """
        Download using HTTrack (recommended)
        
        ✅ Pros:
        - Maximum control
        - Converts links to local
        - Handles everything
        
        ❌ Cons:
        - Requires installation
        """
        if not self._check_tool('httrack'):
            logger.error("❌ httrack not installed!")
            logger.info("   Install: brew install httrack")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = self.download_dir / f"httrack_{timestamp}"
        
        cmd = [
            'httrack',
            url,
            '-O', str(output_dir),
            '-%e',           # Save structure
            '-k',            # Convert links
            '-N100000',      # Max files
            '--max-rate=0',  # No speed limit
            f'-c{self.threads}',  # Threads
            '--continue',    # Continue incomplete
        ]
        
        if self._run_command(cmd, f"HTTrack download to {output_dir}"):
            self._print_result(output_dir)
            return output_dir
        return None
    
    def download_wget(self, url: str) -> Optional[Path]:
        """
        Download using WGET (built-in)
        
        ✅ Pros:
        - Built-in most systems
        - Ultra-fast
        - Simple
        
        ❌ Cons:
        - Less control than httrack
        """
        if not self._check_tool('wget'):
            logger.error("❌ wget not installed!")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = self._get_domain(url)
        output_dir = self.download_dir / f"wget_{timestamp}"
        
        cmd = [
            'wget',
            '--mirror',
            '--page-requisites',
            '--adjust-extension',
            '--span-hosts',
            '--convert-links',
            '--restrict-file-names=windows',
            f'--domains={domain}',
            '--no-parent',
            '--wait=0.5',
            '-P', str(output_dir),
            url
        ]
        
        if self._run_command(cmd, f"WGET download to {output_dir}"):
            self._print_result(output_dir)
            return output_dir
        return None
    
    def download_monolith(self, url: str) -> Optional[Path]:
        """
        Download using Monolith (single file)
        
        ✅ Pros:
        - Single HTML file
        - All embedded
        - Easy to share
        
        ❌ Cons:
        - Larger file
        - Can't edit parts
        """
        if not self._check_tool('monolith'):
            logger.error("❌ monolith not installed!")
            logger.info("   Install: brew install monolith")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = self._get_domain(url)
        output_file = self.download_dir / f"monolith_{domain}_{timestamp}.html"
        
        cmd = [
            'monolith',
            url,
            '-o', str(output_file),
            f'--timeout={self.timeout}'
        ]
        
        if self._run_command(cmd, f"Monolith download to {output_file}"):
            self._print_result(output_file)
            return output_file
        return None
    
    def download_all(self, url: str) -> Dict[str, Optional[Path]]:
        """
        Download using all available methods
        
        Returns:
            Dict with results for each method
        """
        logger.info("\n" + "="*60)
        logger.info("🚀 Downloading with ALL methods...")
        logger.info("="*60 + "\n")
        
        results = {
            'httrack': None,
            'wget': None,
            'monolith': None,
        }
        
        results['httrack'] = self.download_httrack(url)
        logger.info("")
        results['wget'] = self.download_wget(url)
        logger.info("")
        results['monolith'] = self.download_monolith(url)
        
        return results
    
    def download(self, url: str, method: str = 'httrack') -> Optional[Path]:
        """
        Main download method
        
        Args:
            url: Website URL
            method: 'httrack', 'wget', 'monolith', or 'all'
        
        Returns:
            Path to downloaded files or None if failed
        """
        # Validate and format URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        logger.info("\n" + "="*60)
        logger.info(f"🌐 Target URL: {url}")
        logger.info(f"⚙️  Method: {method}")
        logger.info("="*60 + "\n")
        
        if method == 'httrack':
            return self.download_httrack(url)
        elif method == 'wget':
            return self.download_wget(url)
        elif method == 'monolith':
            return self.download_monolith(url)
        elif method == 'all':
            return self.download_all(url)
        else:
            logger.error(f"❌ Unknown method: {method}")
            return None
    
    @staticmethod
    def _print_result(path: Path):
        """Print result information"""
        if path.is_dir():
            size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            files = len(list(path.rglob('*')))
            logger.info(f"\n📂 Downloaded to: {path}")
            logger.info(f"📊 Files: {files}")
            logger.info(f"💾 Size: {size / (1024*1024):.2f} MB")
        else:
            size = path.stat().st_size
            logger.info(f"\n📄 Downloaded to: {path}")
            logger.info(f"💾 Size: {size / (1024*1024):.2f} MB")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🚀 Ultimate Website Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python site_downloader.py https://example.com -m httrack
  python site_downloader.py callmedley.com -m all
  python site_downloader.py https://example.com -m wget --dir ./archives
        """
    )
    
    parser.add_argument('url', help='Website URL to download')
    parser.add_argument(
        '-m', '--method',
        choices=['httrack', 'wget', 'monolith', 'all'],
        default='httrack',
        help='Download method (default: httrack)'
    )
    parser.add_argument(
        '-d', '--dir',
        default='downloads',
        help='Output directory (default: downloads)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    downloader = SiteDownloader(download_dir=args.dir)
    result = downloader.download(args.url, method=args.method)
    
    sys.exit(0 if result else 1)
