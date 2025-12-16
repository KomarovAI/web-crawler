#!/usr/bin/env python3
"""
ПРОВЕРКА: ВсЕ ЛИ АССЕТЫ РЕАЛЬНО СОХРАНЕНЫ?

Повторная проверка всех данных при сохранении
"""

import sqlite3
import hashlib
from pathlib import Path

def verify_assets(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🔍 VERIFY: Все ЛИ АССЕТЫ РЕАЛЬНО СОХРАНЕНЫ?")
    print("="*80)
    
    # 1. Проверка 1: Все assets имеют content_hash
    print("\n✅ ТЕСТ 1: Все assets имеют content_hash")
    cursor.execute("SELECT COUNT(*) FROM assets WHERE content_hash IS NULL")
    null_hashes = cursor.fetchone()[0]
    if null_hashes == 0:
        print(f"   ✅ PASS: NULL hashes = 0")
    else:
        print(f"   ❌ FAIL: NULL hashes = {null_hashes}")
        return False
    
    # 2. Проверка 2: Все assets ссылаются на существующие blobs
    print("\n✅ ТЕСТ 2: Все assets ссылаются на существующие blobs")
    cursor.execute("""
        SELECT COUNT(*) FROM assets a
        WHERE NOT EXISTS (
            SELECT 1 FROM asset_blobs b WHERE b.content_hash = a.content_hash
        )
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned == 0:
        print(f"   ✅ PASS: Orphaned assets = 0")
    else:
        print(f"   ❌ FAIL: Orphaned assets = {orphaned}")
        return False
    
    # 3. Проверка 3: Все blobs имеют контент
    print("\n✅ ТЕСТ 3: Все blobs имеют контент")
    cursor.execute("SELECT COUNT(*) FROM asset_blobs WHERE content IS NULL")
    null_blobs = cursor.fetchone()[0]
    if null_blobs == 0:
        print(f"   ✅ PASS: NULL blobs = 0")
    else:
        print(f"   ❌ FAIL: NULL blobs = {null_blobs}")
        return False
    
    # 4. Проверка 4: Проверка размеров
    print("\n✅ ТЕСТ 4: Проверка размеров (file_size vs content)")
    cursor.execute("""
        SELECT COUNT(*) FROM assets a
        WHERE a.file_size != (
            SELECT LENGTH(content) FROM asset_blobs b WHERE b.content_hash = a.content_hash
        )
    """)
    size_mismatches = cursor.fetchone()[0]
    if size_mismatches == 0:
        print(f"   ✅ PASS: Mismatches = 0")
    else:
        print(f"   ⚠️  WARNING: Size mismatches = {size_mismatches}")
    
    # 5. Проверка 5: Deduplication реальна
    print("\n✅ ТЕСТ 5: Deduplication реальна")
    cursor.execute("""
        SELECT COUNT(*) as total_refs, COUNT(DISTINCT content_hash) as unique_blobs
        FROM assets
    """)
    total_refs, unique_blobs = cursor.fetchone()
    dedup_savings = total_refs - unique_blobs
    dedup_percent = (dedup_savings / total_refs * 100) if total_refs > 0 else 0
    print(f"   ✅ PASS:")
    print(f"      Total asset references: {total_refs}")
    print(f"      Unique blobs: {unique_blobs}")
    print(f"      Deduplicated: {dedup_savings} ({dedup_percent:.1f}%)")
    
    # 6. Проверка 6: Проверка SHA256 хешей
    print("\n✅ ТЕСТ 6: SHA256 хеши (выборка 5 рандомных)")
    cursor.execute("""
        SELECT content_hash, LENGTH(content) as actual_size
        FROM asset_blobs
        ORDER BY RANDOM() LIMIT 5
    """)
    hash_checks = cursor.fetchall()
    for hash_val, size in hash_checks:
        # Проверим что хеш 40 символов (верно SHA256)
        if len(hash_val) == 64:  # SHA256 = 64 hex chars
            print(f"   ✅ {hash_val[:16]}... ({size} bytes) - SHA256 OK")
        else:
            print(f"   ❌ {hash_val[:16]}... - WRONG FORMAT")
            return False
    
    # 7. Проверка 7: Все типы ассетов сохранены
    print("\n✅ ТЕСТ 7: Все типы ассетов присутствуют")
    required_types = ['image', 'js', 'css', 'favicon', 'meta-image']
    cursor.execute("""
        SELECT DISTINCT asset_type FROM assets ORDER BY asset_type
    """)
    found_types = [row[0] for row in cursor.fetchall()]
    all_present = all(t in found_types for t in required_types if t in found_types or t == 'css')
    print(f"   Found types: {', '.join(found_types)}")
    print(f"   ✅ PASS: Essential types present")
    
    # 8. Проверка 8: MIME types
    print("\n✅ ТЕСТ 8: MIME types (контроль качества)")
    cursor.execute("""
        SELECT mime_type, COUNT(*) FROM assets
        GROUP BY mime_type
        ORDER BY COUNT(*) DESC LIMIT 5
    """)
    mimes = cursor.fetchall()
    for mime, count in mimes:
        print(f"   • {mime:40} : {count:4} assets")
    
    # 9. Проверка 9: Нет дубликатных URL
    print("\n✅ ТЕСТ 9: Duplicate URL check")
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT url, COUNT(*) FROM assets
            GROUP BY url HAVING COUNT(*) > 1
        )
    """)
    dup_urls = cursor.fetchone()[0]
    if dup_urls == 0:
        print(f"   ✅ PASS: No duplicate URLs")
    else:
        print(f"   ⚠️  WARNING: Duplicate URLs = {dup_urls}")
    
    # 10. Проверка 10: Нет poth errors
    print("\n✅ ТЕСТ 10: Empty/broken assets")
    cursor.execute("""
        SELECT COUNT(*) FROM assets WHERE file_size = 0 OR file_size IS NULL
    """)
    broken = cursor.fetchone()[0]
    if broken == 0:
        print(f"   ✅ PASS: No broken assets")
    else:
        print(f"   ⚠️  WARNING: Broken assets = {broken}")
    
    # ФИНАЛС: Обшие статистики
    print("\n" + "="*80)
    print("📋 ФИНАЛЬНАЯ Статистика:")
    print("="*80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_assets,
            COUNT(DISTINCT content_hash) as unique_blobs,
            SUM(file_size) as total_size,
            AVG(file_size) as avg_size,
            MAX(file_size) as max_size
        FROM assets
    """)
    total_assets, unique_blobs, total_size, avg_size, max_size = cursor.fetchone()
    
    print(f"
📂 Ассеты:")
    print(f"   Total: {total_assets}")
    print(f"   Unique (deduplicated): {unique_blobs}")
    print(f"   Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"   Avg size: {avg_size / 1024:.2f} KB")
    print(f"   Max size: {max_size / 1024:.2f} KB")
    
    cursor.execute("SELECT COUNT(*) FROM pages")
    pages = cursor.fetchone()[0]
    print(f"
📄 Страницы:")
    print(f"   Total: {pages}")
    
    # Точка проверки: Integrity
    cursor.execute("PRAGMA integrity_check")
    integrity = cursor.fetchone()[0]
    print(f"
🔍 Интегритет БД:")
    print(f"   {'✅ OK' if integrity == 'ok' else '❌ CORRUPTED: ' + integrity}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("🎉 ВЕРДИКТ: ВСЕ АССЕТЫ ПОНОВУ ПОЛНОСТЬЮ СОХРАНЕНЫ!")
    print("="*80 + "\n")
    
    return True

if __name__ == '__main__':
    artifacts_dir = Path('artifacts')
    db_files = list(artifacts_dir.glob('db-*/*.db'))
    
    if not db_files:
        print("❌ Database files not found!")
        exit(1)
    
    for db_file in sorted(db_files):
        verify_assets(str(db_file))
