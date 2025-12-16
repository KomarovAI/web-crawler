#!/usr/bin/env python3
"""
Export archived database to static HTML site
Creates complete website replica from SQLite archive
"""

import sqlite3
import json
from pathlib import Path
from urllib.parse import urlparse, urljoin
import sys

class StaticSiteExporter:
    """Export archived website from SQLite to static HTML files"""
    
    def __init__(self, db_path: str, output_dir: str = 'exported_site'):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def export_all(self):
        """Export complete site"""
        print(f"\n🌐 EXPORTING SITE TO: {self.output_dir}")
        print("="*70)
        
        # 1. Export HTML pages
        self._export_pages()
        
        # 2. Export assets
        self._export_assets()
        
        # 3. Create index
        self._create_index()
        
        # 4. Create sitemap
        self._create_sitemap()
        
        print("="*70)
        print("🌟 EXPORT COMPLETE")
        self.conn.close()
    
    def _export_pages(self):
        """Export all pages from database to HTML files"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pages ORDER BY depth, url')
        
        pages_dir = self.output_dir / 'pages'
        pages_dir.mkdir(exist_ok=True)
        
        count = 0
        for page in cursor.fetchall():
            if page['html_content']:
                # Create file path
                parsed_url = urlparse(page['url'])
                path = parsed_url.path or 'index.html'
                
                if path.endswith('/'):
                    path += 'index.html'
                
                # Create directory structure
                file_path = pages_dir / path.lstrip('/')
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write HTML
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page['html_content'])
                
                print(f"  ✅ {path} ({len(page['html_content'])} bytes)")
                count += 1
        
        print(f"\n📄 Pages exported: {count}")
    
    def _export_assets(self):
        """Export assets (images, CSS, JS, etc.)"""
        cursor = self.conn.cursor()
        
        # Query assets with content
        cursor.execute('''
            SELECT a.url, a.path, ab.content, a.asset_type
            FROM assets a
            JOIN asset_blobs ab ON a.content_hash = ab.content_hash
            ORDER BY a.asset_type, a.path
        ''')
        
        assets_dir = self.output_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        
        count = 0
        for asset in cursor.fetchall():
            # Create file path
            asset_path = asset['path'].lstrip('/')
            file_path = assets_dir / asset_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write binary content
            content = asset['content']
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            print(f"  ✅ [{asset['asset_type']}] {asset['path']}")
            count += 1
        
        print(f"\n📦 Assets exported: {count}")
    
    def _create_index(self):
        """Create index.html with list of pages"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT url, title, depth FROM pages ORDER BY depth, url')
        
        pages = cursor.fetchall()
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archived Site Index</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #333; }
        .pages { list-style: none; padding: 0; }
        .pages li { margin: 10px 0; }
        .pages a { color: #0066cc; text-decoration: none; }
        .pages a:hover { text-decoration: underline; }
        .depth { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🜐 Archived Site Index</h1>
    <p>Total pages: {total}</p>
    
    <ul class="pages">
""".format(total=len(pages))
        
        for page in pages:
            depth_str = f" (depth: {page['depth']})" if page['depth'] > 0 else ""
            html += f"""        <li>
            <a href="pages{urlparse(page['url']).path}">{page['title'] or page['url']}</a>
            <span class="depth">{depth_str}</span>
        </li>\n"""
        
        html += """    </ul>
</body>
</html>
"""
        
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📝 Index created: index.html")
    
    def _create_sitemap(self):
        """Create sitemap.xml"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT domain FROM pages LIMIT 1')
        domain_row = cursor.fetchone()
        domain = f"https://{domain_row['domain']}" if domain_row else "https://archived.site"
        
        cursor.execute('SELECT url, extracted_at FROM pages ORDER BY extracted_at')
        pages = cursor.fetchall()
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for page in pages:
            xml += f'  <url>\n'
            xml += f'    <loc>{page["url"]}</loc>\n'
            xml += f'    <lastmod>{page["extracted_at"]}</lastmod>\n'
            xml += f'  </url>\n'
        
        xml += '</urlset>\n'
        
        with open(self.output_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(xml)
        
        print(f"📋 Sitemap created: sitemap.xml")

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'archive_full.db'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'exported_site'
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    exporter = StaticSiteExporter(db_path, output_dir)
    exporter.export_all()
    
    print(f"\n🚀 Site available at: {output_dir}/index.html")
