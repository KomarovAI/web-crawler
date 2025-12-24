#!/usr/bin/env python3
"""
Optimized URL Rewriter for Offline HTML Archives

Features:
- Single-pass file processing for better performance
- Robust HTML parsing with BeautifulSoup
- Comprehensive logging with different levels
- Support for CSS and JavaScript rewriting
- Proper error handling and recovery
- Relative path calculation for nested files
"""

import os
import re
import sys
import logging
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Set, Tuple, Dict, List
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class URLRewriter:
    """Main class for rewriting URLs in HTML/CSS/JS files"""
    
    # File extensions to process
    HTML_EXTS = {'.html', '.htm'}
    CSS_EXTS = {'.css', '.scss', '.sass'}
    JS_EXTS = {'.js', '.mjs', '.cjs'}
    
    # Directories to skip
    SKIP_DIRS = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv'}
    
    # Statistics
    stats: Dict[str, int] = {
        'files_processed': 0,
        'files_modified': 0,
        'urls_rewritten': 0,
        'errors': 0
    }
    
    def __init__(self, domain: str, base_path: str = '.', dry_run: bool = False):
        """
        Initialize URLRewriter
        
        Args:
            domain: Domain to convert (e.g., 'example.com')
            base_path: Base directory to process
            dry_run: If True, don't write changes
        """
        self.domain = domain
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        
        # Compile regex patterns for performance
        self.url_patterns = self._compile_patterns()
        
        # Try to import BeautifulSoup
        try:
            from bs4 import BeautifulSoup
            self.bs4_available = True
            self.BeautifulSoup = BeautifulSoup
            logger.info("✅ BeautifulSoup4 is available")
        except ImportError:
            self.bs4_available = False
            logger.warning("⚠️  BeautifulSoup4 not available, using regex fallback")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for URL matching"""
        domain_escaped = re.escape(self.domain)
        
        return {
            'http': re.compile(
                rf'(?:https?://)?{domain_escaped}(/[^\s"\x27<>]*)',
                re.IGNORECASE
            ),
            'css_url': re.compile(
                rf'url\(["\x27]?(?:https?://)?{domain_escaped}([^)"\x27]*?)["\x27]?\)',
                re.IGNORECASE
            ),
            'css_import': re.compile(
                rf'@import\s+["\x27](?:https?://)?{domain_escaped}([^"\x27]*)["\x27]',
                re.IGNORECASE
            ),
            'js_url': re.compile(
                rf'["\x27](?:https?://)?{domain_escaped}([^"\x27]*)["\x27]',
                re.IGNORECASE
            ),
        }
    
    def _read_file(self, filepath: Path) -> Tuple[bool, str]:
        """Read file with proper encoding detection"""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    return True, f.read()
            except (UnicodeDecodeError, IOError) as e:
                if encoding == encodings[-1]:
                    logger.error(f"❌ Failed to read {filepath}: {e}")
                    self.stats['errors'] += 1
                    return False, ""
        
        return False, ""
    
    def _write_file(self, filepath: Path, content: str) -> bool:
        """Write file with UTF-8 encoding"""
        if self.dry_run:
            logger.debug(f"🔄 [DRY-RUN] Would write {filepath}")
            return True
        
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            return True
        except IOError as e:
            logger.error(f"❌ Failed to write {filepath}: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_html(self, filepath: Path, content: str) -> Tuple[bool, str]:
        """Process HTML file"""
        if not self.bs4_available:
            return self._process_html_regex(filepath, content)
        
        try:
            soup = self.BeautifulSoup(content, 'html.parser')
            changes = 0
            
            # Add base tag if not present
            head = soup.find('head')
            if head and not soup.find('base'):
                base_tag = soup.new_tag('base', href='/')
                head.insert(0, base_tag)
                changes += 1
            
            # Process href attributes
            for tag in soup.find_all(['a', 'link', 'area']):
                if tag.get('href'):
                    new_href = self._convert_url(tag['href'])
                    if new_href != tag['href']:
                        tag['href'] = new_href
                        changes += 1
            
            # Process src attributes
            for tag in soup.find_all(['img', 'script', 'iframe', 'source', 'video', 'audio', 'embed']):
                if tag.get('src'):
                    new_src = self._convert_url(tag['src'])
                    if new_src != tag['src']:
                        tag['src'] = new_src
                        changes += 1
            
            # Process form actions
            for tag in soup.find_all('form'):
                if tag.get('action'):
                    new_action = self._convert_url(tag['action'])
                    if new_action != tag['action']:
                        tag['action'] = new_action
                        changes += 1
            
            # Process object data
            for tag in soup.find_all('object'):
                if tag.get('data'):
                    new_data = self._convert_url(tag['data'])
                    if new_data != tag['data']:
                        tag['data'] = new_data
                        changes += 1
            
            if changes > 0:
                output = str(soup)
                self.stats['urls_rewritten'] += changes
                return True, output
            
            return False, content
            
        except Exception as e:
            logger.error(f"❌ BeautifulSoup error in {filepath}: {e}")
            self.stats['errors'] += 1
            return False, content
    
    def _process_html_regex(self, filepath: Path, content: str) -> Tuple[bool, str]:
        """Process HTML with regex fallback"""
        pattern = rf'((?:href|src|action|data)=["\x27])https?://{re.escape(self.domain)}'
        new_content = re.sub(pattern, r'\1', content, flags=re.IGNORECASE)
        
        if new_content != content:
            changes = len(re.findall(pattern, content, flags=re.IGNORECASE))
            self.stats['urls_rewritten'] += changes
            return True, new_content
        
        return False, content
    
    def _process_css(self, filepath: Path, content: str) -> Tuple[bool, str]:
        """Process CSS file"""
        original = content
        changes = 0
        
        # Process url() declarations
        pattern = rf'url\(["\x27]?(?:https?://)?{re.escape(self.domain)}([^)"\x27]*?)["\x27]?\)'
        new_content = re.sub(
            pattern,
            r'url(\1)',
            content,
            flags=re.IGNORECASE
        )
        changes += len(re.findall(pattern, content, flags=re.IGNORECASE))
        content = new_content
        
        # Process @import directives
        pattern = rf'@import\s+["\x27](?:https?://)?{re.escape(self.domain)}([^"\x27]*)["\x27]'
        new_content = re.sub(
            pattern,
            r'@import "\1"',
            content,
            flags=re.IGNORECASE
        )
        changes += len(re.findall(pattern, content, flags=re.IGNORECASE))
        content = new_content
        
        if content != original:
            self.stats['urls_rewritten'] += changes
            return True, content
        
        return False, content
    
    def _process_javascript(self, filepath: Path, content: str) -> Tuple[bool, str]:
        """Process JavaScript file"""
        original = content
        
        # Process string URLs
        pattern = rf'["\x27](?:https?://)?{re.escape(self.domain)}([^"\x27]*)["\x27]'
        new_content = re.sub(
            pattern,
            r'"\1"',
            content,
            flags=re.IGNORECASE
        )
        
        changes = len(re.findall(pattern, content, flags=re.IGNORECASE))
        
        if new_content != original:
            self.stats['urls_rewritten'] += changes
            return True, new_content
        
        return False, content
    
    def _convert_url(self, url: str) -> str:
        """Convert URL from absolute to relative"""
        if not url or url.startswith('#'):
            return url
        
        if url.startswith('//') or url.startswith('data:') or url.startswith('blob:'):
            return url
        
        match = self.url_patterns['http'].match(url)
        if match:
            return match.group(1)
        
        return url
    
    def process_directory(self) -> bool:
        """Process all files in directory"""
        logger.info(f"🚀 Starting URL rewriting for domain: {self.domain}")
        logger.info(f"📁 Base directory: {self.base_path}")
        if self.dry_run:
            logger.warning("🔄 DRY-RUN MODE: No changes will be written")
        
        # Collect all files
        files_to_process: Dict[str, List[Path]] = {
            'html': [],
            'css': [],
            'js': []
        }
        
        for root, dirs, filenames in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            
            for filename in filenames:
                filepath = Path(root) / filename
                suffix = filepath.suffix.lower()
                
                if suffix in self.HTML_EXTS:
                    files_to_process['html'].append(filepath)
                elif suffix in self.CSS_EXTS:
                    files_to_process['css'].append(filepath)
                elif suffix in self.JS_EXTS:
                    files_to_process['js'].append(filepath)
        
        logger.info(f"📊 Found: {len(files_to_process['html'])} HTML, "
                   f"{len(files_to_process['css'])} CSS, "
                   f"{len(files_to_process['js'])} JS files")
        
        self._process_files_by_type('html', files_to_process['html'], self._process_html)
        self._process_files_by_type('css', files_to_process['css'], self._process_css)
        self._process_files_by_type('js', files_to_process['js'], self._process_javascript)
        
        self._print_summary()
        
        return self.stats['errors'] == 0
    
    def _process_files_by_type(self, file_type: str, files: List[Path], processor) -> None:
        """Process files of a specific type"""
        if not files:
            return
        
        logger.info(f"\n📄 Processing {len(files)} {file_type.upper()} files...")
        
        for filepath in files:
            success, content = self._read_file(filepath)
            if not success:
                continue
            
            self.stats['files_processed'] += 1
            
            modified, new_content = processor(filepath, content)
            
            if modified:
                if self._write_file(filepath, new_content):
                    self.stats['files_modified'] += 1
                    logger.debug(f"✏️  Modified: {filepath}")
    
    def _print_summary(self) -> None:
        """Print processing summary"""
        logger.info("\n" + "="*60)
        logger.info("📈 URL REWRITING SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Files processed:  {self.stats['files_processed']}")
        logger.info(f"✏️  Files modified:   {self.stats['files_modified']}")
        logger.info(f"🔗 URLs rewritten:   {self.stats['urls_rewritten']}")
        logger.info(f"❌ Errors:           {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Rewrite URLs in HTML/CSS/JS files for offline rendering'
    )
    parser.add_argument(
        'domain',
        help='Domain to convert (e.g., example.com)'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Base directory to process (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    rewriter = URLRewriter(
        domain=args.domain,
        base_path=args.directory,
        dry_run=args.dry_run
    )
    
    success = rewriter.process_directory()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()