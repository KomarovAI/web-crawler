#!/usr/bin/env python3
"""
🕷️ Simple Wget Wrapper for Website Archival
Replaces complex smart_archiver_v4.py with reliable recursive download
"""

import subprocess
import sys
import os
from urllib.parse import urlparse

# --- CONFIGURATION ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# -------------------

def download_site(start_url: str, output_path: str):
    """
    Downloads a website using wget with robust settings.
    
    Args:
        start_url: Full URL to start crawling from (http/https required)
        output_path: Directory where to save downloaded content
    """
    if not start_url.startswith(("http://", "https://")):
        print(f"❌ ERROR: Invalid URL '{start_url}'. Must start with http:// or https://.", file=sys.stderr)
        sys.exit(1)

    domain = urlparse(start_url).netloc
    print(f"🚀 Starting download for: {start_url}")
    print(f"   Domain: {domain}")
    print(f"   Output Path: {output_path}")
    print(f"   User-Agent: {USER_AGENT}")
    print("=" * 70)

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Construct the wget command with production settings
    command = [
        "wget",
        "--recursive",                    # Turn on recursive retrieving
        "--level=inf",                    # Infinite recursion depth (we limit by max_pages separately if needed)
        "--convert-links",                # Make links point to local files
        "--page-requisites",              # Get images, CSS, JS needed for display
        "--adjust-extension",             # Save with proper .html, .css extensions
        "--no-parent",                    # Don't ascend to parent directory
        "--timestamping",                 # Don't re-retrieve unless newer
        "--execute", "robots=off",        # Ignore robots.txt
        "--user-agent", USER_AGENT,       # Proper User-Agent header
        "--timeout=30",                   # Connection timeout
        "--tries=3",                      # Retry failed downloads 3 times
        "--waitretry=5",                  # Wait 5 seconds before retry
        "--random-wait",                  # Random wait between 0-2 seconds
        "--directory-prefix", output_path, # Where to save
        start_url                         # The URL to download
    ]

    try:
        print(f"\n📡 Running: {' '.join(command)}\n")
        
        # Execute wget with real-time output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )

        # Stream output in real time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.rstrip())

        returncode = process.returncode
        
        print("\n" + "=" * 70)
        
        # wget returns 0 on success, 8 for server errors that don't prevent some files being saved
        if returncode not in (0, 8):
            print(f"⚠️ WARNING: wget exited with code {returncode}", file=sys.stderr)
        
        print(f"✅ Download process finished")
        
        # Verify content was actually downloaded
        domain_output_path = os.path.join(output_path, domain)
        
        if not os.path.exists(domain_output_path):
            print(f"\n❌ ERROR: Expected output directory '{domain_output_path}' was not created", file=sys.stderr)
            print(f"\n📂 Contents of '{output_path}':")
            for item in os.listdir(output_path):
                print(f"   {item}")
            sys.exit(1)
        
        if not os.listdir(domain_output_path):
            print(f"\n❌ ERROR: Output directory '{domain_output_path}' is empty", file=sys.stderr)
            print(f"   Site may be blocking crawlers or requires JavaScript rendering", file=sys.stderr)
            sys.exit(1)
        
        # Count files
        file_count = sum(1 for _ in os.walk(domain_output_path) for _ in _[2])
        total_size = sum(
            f.stat().st_size for f in __import__('pathlib').Path(domain_output_path).rglob('*') if f.is_file()
        ) / (1024 * 1024)  # Convert to MB
        
        print(f"\n✅ ARCHIVE VERIFIED")
        print(f"   Path: {domain_output_path}")
        print(f"   Files downloaded: {file_count}")
        print(f"   Total size: {total_size:.2f} MB")
        print("=" * 70)

    except FileNotFoundError:
        print("❌ ERROR: wget is not installed. Install with: sudo apt-get install wget", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 crawler.py <URL> <output_directory>", file=sys.stderr)
        print("Example: python3 crawler.py https://example.com output", file=sys.stderr)
        sys.exit(1)
    
    url_to_crawl = sys.argv[1]
    output_dir = sys.argv[2]
    download_site(url_to_crawl, output_dir)
