#!/usr/bin/env python3
"""
Rewrite links in HTML files to use local paths instead of absolute URLs.
Usage: python3 rewrite_links.py /path/to/directory domain.com
"""

import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, quote, unquote

def normalize_path(path):
    """Normalize path - remove leading/trailing slashes, ensure consistency"""
    path = unquote(path)
    path = path.strip('/')
    if not path or path == 'index.html':
        return 'index.html'
    if path.endswith('/'):
        path = path + 'index.html'
    elif not path.endswith('.html') and not '.' in path.split('/')[-1]:
        path = path + '/index.html'
    return path

def should_rewrite_url(url, domain):
    """Check if URL should be rewritten to local path"""
    if not url or url.startswith('#') or url.startswith('javascript:') or url.startswith('mailto:') or url.startswith('tel:'):
        return False
    
    # Check if URL is for the same domain
    if domain in url:
        return True
    
    # Check if it's a path-only URL
    if url.startswith('/'):
        return True
    
    # Check if it's a relative URL
    if not url.startswith('http://') and not url.startswith('https://') and not url.startswith('//'):
        return True
    
    return False

def rewrite_url(url, domain):
    """Convert absolute URL to relative path"""
    if not should_rewrite_url(url, domain):
        return url
    
    # Remove protocol and domain
    if f'https://{domain}' in url:
        path = url.split(f'https://{domain}', 1)[1]
    elif f'http://{domain}' in url:
        path = url.split(f'http://{domain}', 1)[1]
    elif url.startswith('//'):
        # Protocol-relative URL
        parts = url.split('/', 3)
        if len(parts) > 3 and domain in parts[2]:
            path = '/' + parts[3]
        else:
            return url
    else:
        path = url
    
    # Remove query parameters and fragments for path matching
    path_only = path.split('?')[0].split('#')[0]
    fragment = url.split('#', 1)[1] if '#' in url else ''
    query = '?' + url.split('?', 1)[1] if '?' in url else ''
    
    # Normalize the path
    normalized = normalize_path(path_only)
    
    # Reconstruct URL with query and fragment
    result = normalized
    if query:
        result += query
    if fragment:
        result += '#' + fragment
    
    # Convert to relative path
    if result.startswith('/'):
        result = result[1:]
    
    return result

def process_html_file(filepath, domain):
    """Process single HTML file and rewrite links"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Error reading {filepath}: {e}")
        return False
    
    original_content = content
    
    # Regex patterns for different link types
    patterns = [
        # href="..." attributes
        (r'href=["\']([^"\'>]+)["\']', 'href'),
        # src="..." attributes
        (r'src=["\']([^"\'>]+)["\']', 'src'),
        # data-href="..." attributes
        (r'data-href=["\']([^"\'>]+)["\']', 'data-href'),
        # action="..." in forms
        (r'action=["\']([^"\'>]+)["\']', 'action'),
        # content="..." in meta tags
        (r'content=["\']([^"\'>]+)["\']', 'content'),
        # @import in CSS
        (r'@import\s+["\']([^"\'>]+)["\']', 'css-import'),
    ]
    
    changes = 0
    for pattern, attr_type in patterns:
        def replace_url(match):
            nonlocal changes
            url = match.group(1)
            
            # Skip data URIs, blobs, etc.
            if url.startswith('data:') or url.startswith('blob:'):
                return match.group(0)
            
            new_url = rewrite_url(url, domain)
            if new_url != url:
                changes += 1
                quote = '\"' if '\"' in match.group(0) else "'"
                attr_name = attr_type.split('-')[0]
                return f'{attr_name}={quote}{new_url}{quote}'
            return match.group(0)
        
        content = re.sub(pattern, replace_url, content, flags=re.IGNORECASE)
    
    # Write back if changed
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✏️  {filepath}: {changes} links rewritten")
            return True
        except Exception as e:
            print(f"  ❌ Error writing {filepath}: {e}")
            return False
    
    return False

def process_directory(root_dir, domain):
    """Recursively process all HTML files in directory"""
    total_files = 0
    modified_files = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.lower().endswith('.html'):
                filepath = os.path.join(root, file)
                total_files += 1
                if process_html_file(filepath, domain):
                    modified_files += 1
    
    return total_files, modified_files

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 rewrite_links.py /path/to/directory domain.com")
        print("\nExample: python3 rewrite_links.py . callmedley.com")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    domain = sys.argv[2]
    
    # Remove www. prefix if present
    domain = domain.replace('www.', '')
    
    print(f"🔄 Rewriting links in {root_dir}")
    print(f"📍 Domain: {domain}")
    print()
    
    if not os.path.isdir(root_dir):
        print(f"❌ Directory not found: {root_dir}")
        sys.exit(1)
    
    total, modified = process_directory(root_dir, domain)
    
    print()
    print(f"✅ Complete!")
    print(f"📊 Total HTML files: {total}")
    print(f"✏️  Modified files: {modified}")

if __name__ == '__main__':
    main()
