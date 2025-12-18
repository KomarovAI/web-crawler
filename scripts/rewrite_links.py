#!/usr/bin/env python3
"""
Link Rewriting Utility
Converts absolute URLs to relative paths for offline archives.
"""

import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, unquote


def normalize_path(path):
    """Normalize path to proper file structure."""
    path = unquote(path)
    path = path.strip('/')
    if not path or path == 'index.html':
        return 'index.html'
    if path.endswith('/'):
        path = path + 'index.html'
    elif not path.endswith('.html') and '.' not in path.split('/')[-1]:
        path = path + '/index.html'
    return path


def should_rewrite_url(url, domain):
    """Check if URL should be rewritten."""
    if not url:
        return False
    if url.startswith('#') or url.startswith('javascript:'):
        return False
    if url.startswith('mailto:') or url.startswith('tel:'):
        return False
    if url.startswith('data:') or url.startswith('blob:'):
        return False
    if domain in url:
        return True
    if url.startswith('/'):
        return True
    if not url.startswith('http://') and not url.startswith('https://') and not url.startswith('//'):
        return True
    return False


def rewrite_url(url, domain):
    """Rewrite URL to relative path."""
    if not should_rewrite_url(url, domain):
        return url
    
    # Extract path from absolute URL
    if f'https://{domain}' in url:
        path = url.split(f'https://{domain}', 1)[1]
    elif f'http://{domain}' in url:
        path = url.split(f'http://{domain}', 1)[1]
    else:
        path = url
    
    # Preserve query string and fragment
    path_only = path.split('?')[0].split('#')[0]
    fragment = url.split('#', 1)[1] if '#' in url else ''
    query = '?' + url.split('?', 1)[1] if '?' in url else ''
    
    # Normalize and reconstruct
    normalized = normalize_path(path_only)
    result = normalized
    if query:
        result += query
    if fragment:
        result += '#' + fragment
    if result.startswith('/'):
        result = result[1:]
    return result


def process_html_file(filepath, domain):
    """Process HTML file and rewrite URLs."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Skip {filepath}: {e}")
        return False
    
    original_content = content
    patterns = [
        (r'href=["\']([^"\'>]+)["\']', 'href'),
        (r'src=["\']([^"\'>]+)["\']', 'src'),
        (r'action=["\']([^"\'>]+)["\']', 'action'),
    ]
    
    for pattern, attr_type in patterns:
        def replace_url(match):
            url = match.group(1)
            if url.startswith('data:') or url.startswith('blob:'):
                return match.group(0)
            new_url = rewrite_url(url, domain)
            if new_url != url:
                quote = '"' if '"' in match.group(0) else "'"
                attr_name = attr_type.split('-')[0]
                return f'{attr_name}={quote}{new_url}{quote}'
            return match.group(0)
        content = re.sub(pattern, replace_url, content, flags=re.IGNORECASE)
    
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"⚠️  Failed to write {filepath}: {e}")
            return False
    return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        domain = os.environ.get('DOMAIN', 'example.com')
        root_dir = '.'
    else:
        domain = sys.argv[1]
        root_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    print(f"🔗 Rewriting URLs for domain: {domain}")
    print(f"📁 Processing directory: {root_dir}")
    
    total = 0
    modified = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.lower().endswith('.html'):
                filepath = os.path.join(root, file)
                total += 1
                if process_html_file(filepath, domain):
                    modified += 1
                    print(f"✅ {filepath}")
    
    print(f"\n📊 Results: {total} HTML files, {modified} modified")
    return 0 if modified >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
