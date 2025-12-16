#!/usr/bin/env python3
"""
Local test script to verify asset extraction
"""

import asyncio
import aiohttp
from asset_extractor import AssetExtractor
import sqlite3

async def test():
    # Create in-memory DB
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE asset_blobs (
            id INTEGER PRIMARY KEY,
            content_hash TEXT UNIQUE NOT NULL,
            content BLOB NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            path TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            content_hash TEXT UNIQUE NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Create extractor
    extractor = AssetExtractor(conn)
    
    # Test HTML
    html = '''
    <html>
    <head>
        <link rel="stylesheet" href="https://callmedley.com/style.css">
        <script src="https://callmedley.com/script.js"></script>
    </head>
    <body>
        <img src="https://callmedley.com/image.png" alt="test">
    </body>
    </html>
    '''
    
    # Extract assets
    assets = extractor.extract_assets(html, 'https://callmedley.com')
    print(f"Found {len(assets)} assets:")
    for asset in assets:
        print(f"  - {asset['type']}: {asset['url']}")
    
    # Simulate download
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for asset in assets[:1]:  # Download first asset only
            result = await extractor.download_and_save_asset(asset, 'callmedley.com', session)
            print(f"\nDownload result: {result}")
    
    # Check DB
    cursor.execute('SELECT COUNT(*) FROM assets')
    print(f"Assets in DB: {cursor.fetchone()[0]}")
    
    conn.close()

if __name__ == '__main__':
    asyncio.run(test())
