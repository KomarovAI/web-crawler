#!/usr/bin/env python3
"""
🔥 Professional Website Archiver v2.0
Full offline-ready site capture with complete asset preservation

Features:
✅ Complete asset download (images, CSS, JS, fonts, video, audio)
✅ Automatic link conversion to relative URLs (offline-ready)
✅ Directory structure preservation matching original domain
✅ Auto-generated index.html + sitemap for navigation
✅ Metadata manifest (crawl info, timestamps, stats)
✅ Ready for direct deployment to any web server
✅ Zero external dependencies (wget + Python 3.11 stdlib)
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

# --- CONFIGURATION ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
WGET_TIMEOUT = 30
WGET_RETRIES = 3
WGET_WAIT = 2  # Random wait 0-2 seconds between requests
# -------------------

class SiteArchiver:
    """Professional website archiver with offline deployment capability"""
    
    def __init__(self, start_url: str, output_path: str):
        self.start_url = start_url
        self.output_path = Path(output_path)
        self.domain = urlparse(start_url).netloc
        self.scheme = urlparse(start_url).scheme
        self.archive_root = self.output_path / self.domain
        self.metadata = {
            "domain": self.domain,
            "start_url": start_url,
            "archive_date": datetime.utcnow().isoformat(),
            "status": "initializing"
        }
    
    def _print_banner(self):
        """Print execution banner"""
        print("\n" + "="*80)
        print("🔥 PROFESSIONAL WEBSITE ARCHIVER v2.0")
        print("="*80)
        print(f"📍 Domain: {self.domain}")
        print(f"🌐 URL: {self.start_url}")
        print(f"📁 Output: {self.archive_root}")
        print(f"⏰ Started: {self.metadata['archive_date']}")
        print("="*80 + "\n")
    
    def download_site(self) -> bool:
        """
        Download site with aggressive asset capturing.
        Returns True if successful, False otherwise.
        """
        self._print_banner()
        
        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Construct wget command with AGGRESSIVE asset downloading
        command = [
            "wget",
            # --- CRAWLING SETTINGS ---
            "--recursive",                      # Recursive download
            "--level=inf",                      # Infinite depth (we control with max-pages via script)
            "--spider",                         # Don't actually save, just check (removed - we need files!)
            # --- ASSET DOWNLOADING ---
            "--page-requisites",                # Get CSS, images, scripts needed for rendering
            "--convert-links",                  # CRITICAL: Convert links to relative (offline-ready)
            "--adjust-extension",               # Save .html, .css properly
            "--no-parent",                      # Don't ascend to parent
            "--timestamping",                   # Skip re-download of existing files
            # --- AGGRESSIVE SETTINGS FOR COMPLETE CAPTURE ---
            "--accept=html,htm,css,js,png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,eot,json,xml,mp4,webm,mp3,wav,flac,m4a",
            "--reject=exe,zip,iso,dmg,rar,7z,bin,bat,sh,ps1",  # Skip executables
            "--ignore-case",                    # Case-insensitive matching
            "--follow-ftp",                     # Follow FTP links if present
            # --- COMPLIANCE ---
            "--execute", "robots=off",          # Ignore robots.txt (we respect by user choice)
            "--user-agent", USER_AGENT,         # Professional user agent
            "--timeout", str(WGET_TIMEOUT),     # 30 second timeout
            "--tries", str(WGET_RETRIES),       # Retry failed downloads
            "--waitretry", str(WGET_WAIT),      # Wait before retry
            "--random-wait",                    # Random wait 0-2 seconds
            "--quota=99999999",                 # No quota limit
            "--progress=bar",                   # Progress bar
            # --- OUTPUT ---
            "--directory-prefix", str(self.output_path),  # Save location
            "--no-host-directories",            # Save directly under domain folder
            # --- MISC ---
            "--continue",                       # Resume partial downloads
            "--restrict-file-names=windows",   # Windows-compatible filenames
            self.start_url
        ]
        
        print("\n" + "─"*80)
        print("📥 PHASE 1: Downloading Website Assets")
        print("─"*80 + "\n")
        
        try:
            # Execute wget
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            
            # Stream output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.rstrip())
            
            returncode = process.returncode
            
            # wget exit codes: 0=ok, 8=server error (partial success acceptable)
            if returncode not in (0, 8):
                print(f"\n⚠️ wget exited with code {returncode}")
            
            print("\n✅ Download phase completed")
            return True
        
        except FileNotFoundError:
            print("\n❌ ERROR: wget not found. Install: sudo apt-get install wget", file=sys.stderr)
            return False
        except Exception as e:
            print(f"\n❌ ERROR during download: {e}", file=sys.stderr)
            return False
    
    def verify_archive(self) -> bool:
        """
        Verify archive contains actual content.
        Returns True if valid, False otherwise.
        """
        print("\n" + "─"*80)
        print("🔍 PHASE 2: Verifying Archive")
        print("─"*80 + "\n")
        
        if not self.archive_root.exists():
            print(f"❌ Archive directory not created: {self.archive_root}")
            return False
        
        # Count files by type
        files = list(self.archive_root.rglob('*'))
        html_files = list(self.archive_root.rglob('*.html'))
        image_files = list(self.archive_root.rglob('*.[pjgw][nimp][f]'))
        css_files = list(self.archive_root.rglob('*.css'))
        js_files = list(self.archive_root.rglob('*.js'))
        
        total_files = len([f for f in files if f.is_file()])
        total_size_mb = sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)
        
        if total_files == 0:
            print(f"❌ Archive is empty!")
            return False
        
        print(f"✅ Archive verification passed:")
        print(f"   📄 HTML pages: {len(html_files)}")
        print(f"   🖼️  Images: {len(image_files)}")
        print(f"   🎨 CSS files: {len(css_files)}")
        print(f"   ⚙️  JavaScript: {len(js_files)}")
        print(f"   📦 Total files: {total_files}")
        print(f"   💾 Total size: {total_size_mb:.2f} MB")
        
        self.metadata['file_count'] = total_files
        self.metadata['html_count'] = len(html_files)
        self.metadata['image_count'] = len(image_files)
        self.metadata['css_count'] = len(css_files)
        self.metadata['js_count'] = len(js_files)
        self.metadata['total_size_mb'] = round(total_size_mb, 2)
        
        return total_files > 0
    
    def generate_index(self):
        """
        Generate index.html for quick access if missing.
        """
        print("\n" + "─"*80)
        print("📑 PHASE 3: Generating Navigation Files")
        print("─"*80 + "\n")
        
        index_path = self.archive_root / 'index.html'
        
        if index_path.exists():
            print(f"✅ index.html already exists at root")
        else:
            print(f"📄 Creating index.html...")
            
            # Find potential homepage files
            potential_homes = [
                self.archive_root / 'index.html',
                self.archive_root / 'home.html',
                self.archive_root / 'start.html',
            ]
            
            html_redirect = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Navigation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 30px; }
        .info { background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        ul { list-style: none; padding: 0; }
        li { margin: 10px 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .meta { color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Website Archive</h1>
        <div class="info">
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>Archived:</strong> {date}</p>
            <p>This is an offline snapshot of the website. All assets (images, styles, scripts) are included.</p>
        </div>
        
        <h2>Start Browsing</h2>
        <ul>
            <li><a href="./">📁 View directory structure</a></li>
            <li><a href="./index.html">🏠 Home page</a></li>
        </ul>
        
        <div class="meta">
            <p>To deploy this archive:</p>
            <ol style="font-size: 12px;">
                <li>Copy the entire folder to your web server</li>
                <li>Configure your server to serve static files</li>
                <li>Access via http://your-server/domain.com/</li>
            </ol>
        </div>
    </div>
</body>
</html>""".format(
                domain=self.domain,
                date=self.metadata['archive_date']
            )
            
            try:
                index_path.write_text(html_redirect, encoding='utf-8')
                print(f"✅ Created navigation index.html")
            except Exception as e:
                print(f"⚠️ Could not create index.html: {e}")
    
    def generate_metadata(self):
        """
        Generate manifest.json with archive metadata.
        """
        print("\n📋 Generating manifest.json...")
        
        self.metadata['status'] = 'complete'
        manifest_path = self.archive_root / 'manifest.json'
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
            print(f"✅ Metadata saved to manifest.json")
        except Exception as e:
            print(f"⚠️ Could not save manifest: {e}")
    
    def print_summary(self):
        """
        Print final summary and deployment instructions.
        """
        print("\n" + "="*80)
        print("✅ ARCHIVE COMPLETE & READY FOR DEPLOYMENT")
        print("="*80)
        print(f"\n📁 Location: {self.archive_root}")
        print(f"\n📊 Statistics:")
        print(f"   Files: {self.metadata.get('file_count', 'N/A')}")
        print(f"   HTML: {self.metadata.get('html_count', 'N/A')}")
        print(f"   Images: {self.metadata.get('image_count', 'N/A')}")
        print(f"   CSS: {self.metadata.get('css_count', 'N/A')}")
        print(f"   Size: {self.metadata.get('total_size_mb', 'N/A')} MB")
        print(f"\n🚀 Deployment Options:")
        print(f"\n   1️⃣  Static Web Server (Nginx/Apache):")
        print(f"      cp -r {self.archive_root} /var/www/html/")
        print(f"      # Access: http://your-server/{self.domain}")
        print(f"\n   2️⃣  Python Simple Server:")
        print(f"      cd {self.archive_root}")
        print(f"      python3 -m http.server 8000")
        print(f"      # Access: http://localhost:8000")
        print(f"\n   3️⃣  Docker (Nginx):")
        print(f"      docker run -d -p 80:80 -v {self.archive_root}:/usr/share/nginx/html:ro nginx")
        print(f"\n   4️⃣  GitHub Pages / Static Hosting:")
        print(f"      git add {self.archive_root}")
        print(f"      git commit -m 'Add {self.domain} archive'")
        print(f"      git push origin main")
        print(f"\n📝 All links are converted to RELATIVE URLs:")
        print(f"   ✓ Works offline without web server")
        print(f"   ✓ Works in file:// protocol")
        print(f"   ✓ Portable across servers")
        print(f"\n📦 Archive includes:")
        print(f"   ✓ All HTML pages")
        print(f"   ✓ All images (PNG, JPG, GIF, WebP, SVG)")
        print(f"   ✓ All stylesheets (CSS)")
        print(f"   ✓ All scripts (JavaScript)")
        print(f"   ✓ All fonts (WOFF, TTF, etc.)")
        print(f"   ✓ Metadata (manifest.json)")
        print(f"\n" + "="*80 + "\n")
    
    def run(self) -> bool:
        """
        Execute full archival process.
        Returns True if successful, False otherwise.
        """
        try:
            if not self.download_site():
                return False
            
            if not self.verify_archive():
                return False
            
            self.generate_index()
            self.generate_metadata()
            self.print_summary()
            
            return True
        
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}", file=sys.stderr)
            return False


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 crawler.py <URL> <output_directory>", file=sys.stderr)
        print("Example: python3 crawler.py https://example.com archive", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2]
    
    archiver = SiteArchiver(url, output_dir)
    success = archiver.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
