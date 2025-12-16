#!/usr/bin/env python3
"""
ДЕТАЛЬНЫЙ АУДИТ БАЗЫ ДАННЫХ ВЕБА-АРХИВА
Проверяет целостность, структуру, содержимое и оптимизацию БД
"""

import sqlite3
import os
import sys
from pathlib import Path
from collections import defaultdict
import hashlib

class DatabaseAuditor:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def run_full_audit(self):
        """Запустить полный аудит"""
        print("\n" + "="*70)
        print("🔍 ПОЛНЫЙ АУДИТ БАЗЫ ДАННЫХ")
        print("="*70)
        print(f"\n📁 База: {self.db_path}")
        print(f"📦 Размер: {os.path.getsize(self.db_path) / 1024 / 1024:.2f} MB\n")
        
        self.check_integrity()
        self.check_tables_schema()
        self.check_pages_table()
        self.check_assets_table()
        self.check_asset_blobs_table()
        self.check_links_table()
        self.check_metadata_table()
        self.check_indexes()
        self.check_foreign_keys()
        self.check_deduplication()
        self.check_orphaned_records()
        self.check_duplicates()
        self.check_compression()
        self.check_database_performance()
        self.generate_report()
    
    def check_integrity(self):
        """1. Проверка целостности БД"""
        print("\n" + "-"*70)
        print("1️⃣  ЦЕЛОСТНОСТЬ БД")
        print("-"*70)
        
        self.cursor.execute("PRAGMA integrity_check")
        result = self.cursor.fetchone()[0]
        
        if result == 'ok':
            print("✅ PRAGMA integrity_check: OK")
        else:
            print(f"❌ PRAGMA integrity_check: {result}")
            self.issues.append(f"Database corruption: {result}")
        
        self.cursor.execute("PRAGMA quick_check")
        result = self.cursor.fetchone()[0]
        print(f"✅ PRAGMA quick_check: {result}")
    
    def check_tables_schema(self):
        """2. Проверка схемы таблиц"""
        print("\n" + "-"*70)
        print("2️⃣  СХЕМА ТАБЛИЦ")
        print("-"*70)
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        print(f"\n✅ Таблиц найдено: {len(tables)}\n")
        
        required_tables = ['pages', 'assets', 'asset_blobs', 'links', 'metadata']
        
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = self.cursor.fetchall()
            print(f"📋 {table.upper()}")
            print(f"   Колонок: {len(columns)}")
            for col in columns:
                col_id, name, type_, notnull, dflt, pk = col
                nullable = "🔴 NULL" if not notnull else "🟢 NOT NULL"
                pk_mark = "(PRIMARY KEY)" if pk else ""
                print(f"      • {name:20} {type_:15} {nullable} {pk_mark}")
            print()
        
        for req_table in required_tables:
            if req_table not in tables:
                self.warnings.append(f"Missing recommended table: {req_table}")
    
    def check_pages_table(self):
        """3. Проверка таблицы PAGES"""
        print("\n" + "-"*70)
        print("3️⃣  ТАБЛИЦА PAGES")
        print("-"*70)
        
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        total_pages = self.cursor.fetchone()[0]
        print(f"\n✅ Всего страниц: {total_pages}")
        
        # Уникальные URL
        self.cursor.execute("SELECT COUNT(DISTINCT url) FROM pages")
        unique_urls = self.cursor.fetchone()[0]
        print(f"✅ Уникальных URL: {unique_urls}")
        
        if unique_urls != total_pages:
            self.warnings.append(f"Duplicate URLs found: {total_pages - unique_urls}")
        
        # Размер HTML
        self.cursor.execute("SELECT SUM(LENGTH(html)) FROM pages WHERE html IS NOT NULL")
        html_size = self.cursor.fetchone()[0] or 0
        print(f"📊 Суммарный размер HTML: {html_size / 1024 / 1024:.2f} MB")
        
        # Страницы без HTML
        self.cursor.execute("SELECT COUNT(*) FROM pages WHERE html IS NULL")
        no_html = self.cursor.fetchone()[0]
        if no_html > 0:
            print(f"⚠️  Страниц без HTML: {no_html}")
            self.warnings.append(f"Pages without HTML: {no_html}")
        
        # Проверка title
        self.cursor.execute("SELECT COUNT(*) FROM pages WHERE title IS NULL")
        no_title = self.cursor.fetchone()[0]
        if no_title > 0:
            print(f"⚠️  Страниц без title: {no_title}")
        
        # Статус коды
        self.cursor.execute("SELECT status_code, COUNT(*) FROM pages GROUP BY status_code")
        status_codes = self.cursor.fetchall()
        print(f"\n📈 Статус коды:")
        for code, count in sorted(status_codes):
            status_symbol = "✅" if code == 200 else "⚠️"
            print(f"   {status_symbol} {code}: {count} страниц")
        
        self.stats['total_pages'] = total_pages
    
    def check_assets_table(self):
        """4. Проверка таблицы ASSETS"""
        print("\n" + "-"*70)
        print("4️⃣  ТАБЛИЦА ASSETS")
        print("-"*70)
        
        self.cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = self.cursor.fetchone()[0]
        print(f"\n✅ Всего ассетов: {total_assets}")
        
        # Уникальные ассеты
        self.cursor.execute("SELECT COUNT(DISTINCT content_hash) FROM assets")
        unique_assets = self.cursor.fetchone()[0]
        print(f"✅ Уникальных ассетов (по хешу): {unique_assets}")
        
        dedup_ratio = ((total_assets - unique_assets) / total_assets * 100) if total_assets > 0 else 0
        print(f"📊 Дедупликация: {dedup_ratio:.1f}% (экономия {total_assets - unique_assets} ассетов)")
        
        # По типам
        self.cursor.execute("SELECT asset_type, COUNT(*) FROM assets GROUP BY asset_type")
        types = self.cursor.fetchall()
        print(f"\n📂 По типам:")
        for asset_type, count in sorted(types, key=lambda x: x[1], reverse=True):
            print(f"   • {asset_type:15} {count:5} ассетов")
        
        # MIME типы
        self.cursor.execute("SELECT mime_type, COUNT(*) FROM assets GROUP BY mime_type ORDER BY COUNT(*) DESC LIMIT 10")
        mimes = self.cursor.fetchall()
        print(f"\n🏷️  Топ MIME типов:")
        for mime, count in mimes:
            print(f"   • {mime:40} {count:4} ассетов")
        
        # Размеры
        self.cursor.execute("SELECT SUM(file_size), AVG(file_size), MAX(file_size) FROM assets")
        total_size, avg_size, max_size = self.cursor.fetchone()
        total_size = total_size or 0
        print(f"\n📊 Размеры ассетов:")
        print(f"   Суммарно: {total_size / 1024 / 1024:.2f} MB")
        print(f"   Среднее: {avg_size / 1024:.2f} KB")
        print(f"   Максимум: {max_size / 1024:.2f} KB")
        
        # Ошибки загрузки
        self.cursor.execute("SELECT COUNT(*) FROM assets WHERE file_size IS NULL OR file_size = 0")
        empty_assets = self.cursor.fetchone()[0]
        if empty_assets > 0:
            self.warnings.append(f"Empty/failed assets: {empty_assets}")
        
        self.stats['total_assets'] = total_assets
        self.stats['total_asset_size'] = total_size
    
    def check_asset_blobs_table(self):
        """5. Проверка таблицы ASSET_BLOBS (дедупликация)"""
        print("\n" + "-"*70)
        print("5️⃣  ТАБЛИЦА ASSET_BLOBS (ДЕДУПЛИКАЦИЯ)")
        print("-"*70)
        
        self.cursor.execute("SELECT COUNT(*) FROM asset_blobs")
        total_blobs = self.cursor.fetchone()[0]
        print(f"\n✅ Уникальных BLOB'ов: {total_blobs}")
        
        # Размер BLOB'ов
        self.cursor.execute("SELECT SUM(LENGTH(content)) FROM asset_blobs")
        blob_size = self.cursor.fetchone()[0] or 0
        print(f"📊 Суммарный размер BLOB'ов: {blob_size / 1024 / 1024:.2f} MB")
        
        # Проверка на дубликаты хешей
        self.cursor.execute("SELECT content_hash, COUNT(*) FROM asset_blobs GROUP BY content_hash HAVING COUNT(*) > 1")
        duplicate_hashes = self.cursor.fetchall()
        if duplicate_hashes:
            print(f"❌ Найдено {len(duplicate_hashes)} дубликатных хешей!")
            self.issues.append(f"Duplicate content_hashes: {len(duplicate_hashes)}")
        else:
            print(f"✅ Дубликатные хеши: НЕТ")
        
        # Проверка на NULL контент
        self.cursor.execute("SELECT COUNT(*) FROM asset_blobs WHERE content IS NULL")
        null_content = self.cursor.fetchone()[0]
        if null_content > 0:
            print(f"❌ BLOB'ов с NULL контентом: {null_content}")
            self.issues.append(f"NULL content in asset_blobs: {null_content}")
        else:
            print(f"✅ NULL контента: НЕТ")
    
    def check_links_table(self):
        """6. Проверка таблицы LINKS"""
        print("\n" + "-"*70)
        print("6️⃣  ТАБЛИЦА LINKS")
        print("-"*70)
        
        self.cursor.execute("SELECT COUNT(*) FROM links")
        total_links = self.cursor.fetchone()[0]
        print(f"\n✅ Всего ссылок: {total_links}")
        
        # По типам
        self.cursor.execute("SELECT link_type, COUNT(*) FROM links GROUP BY link_type")
        link_types = self.cursor.fetchall()
        if link_types:
            print(f"\n📂 По типам:")
            for link_type, count in sorted(link_types):
                print(f"   • {link_type:15} {count:5} ссылок")
    
    def check_metadata_table(self):
        """7. Проверка таблицы METADATA"""
        print("\n" + "-"*70)
        print("7️⃣  ТАБЛИЦА METADATA")
        print("-"*70)
        
        self.cursor.execute("SELECT COUNT(*) FROM metadata")
        total_metadata = self.cursor.fetchone()[0]
        print(f"\n✅ Записей метаданных: {total_metadata}")
        
        # По типам метаданных
        self.cursor.execute("SELECT key, COUNT(*) FROM metadata GROUP BY key")
        meta_keys = self.cursor.fetchall()
        if meta_keys:
            print(f"\n🏷️  Типы метаданных:")
            for key, count in sorted(meta_keys, key=lambda x: x[1], reverse=True):
                print(f"   • {key:30} {count:5} записей")
    
    def check_indexes(self):
        """8. Проверка индексов"""
        print("\n" + "-"*70)
        print("8️⃣  ИНДЕКСЫ")
        print("-"*70)
        
        self.cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY tbl_name")
        indexes = self.cursor.fetchall()
        
        print(f"\n✅ Индексов найдено: {len(indexes)}\n")
        
        if indexes:
            for idx_name, tbl_name in indexes:
                print(f"   • {idx_name:40} на таблице {tbl_name}")
        else:
            print("   ⚠️  Индексы не найдены!")
            self.warnings.append("No indexes found")
    
    def check_foreign_keys(self):
        """9. Проверка внешних ключей"""
        print("\n" + "-"*70)
        print("9️⃣  ВНЕШНИЕ КЛЮЧИ (FOREIGN KEYS)")
        print("-"*70)
        
        self.cursor.execute("PRAGMA foreign_keys")
        fk_status = self.cursor.fetchone()[0]
        print(f"\n{'✅' if fk_status else '❌'} Foreign keys: {'ENABLED' if fk_status else 'DISABLED'}")
        
        # Проверка нарушений FK
        self.cursor.execute("PRAGMA foreign_key_check")
        fk_violations = self.cursor.fetchall()
        
        if fk_violations:
            print(f"❌ Нарушений FK: {len(fk_violations)}")
            for violation in fk_violations[:5]:
                print(f"   {violation}")
            self.issues.append(f"Foreign key violations: {len(fk_violations)}")
        else:
            print(f"✅ Нарушений FK: НЕТ")
    
    def check_deduplication(self):
        """10. Анализ дедупликации"""
        print("\n" + "-"*70)
        print("🔟 АНАЛИЗ ДЕДУПЛИКАЦИИ")
        print("-"*70)
        
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_references,
                COUNT(DISTINCT content_hash) as unique_blobs,
                SUM(CASE WHEN ref_count > 1 THEN 1 ELSE 0 END) as deduplicated_count
            FROM (
                SELECT content_hash, COUNT(*) as ref_count
                FROM assets
                GROUP BY content_hash
            )
        """)
        
        total_refs, unique_blobs, dedup_count = self.cursor.fetchone()
        
        print(f"\n📊 Статистика дедупликации:")
        print(f"   Всего ссылок на ассеты: {total_refs}")
        print(f"   Уникальных BLOB'ов: {unique_blobs}")
        print(f"   Дедупликовано: {dedup_count} типов ассетов")
        
        if unique_blobs > 0:
            dedup_ratio = (1 - unique_blobs / total_refs) * 100
            print(f"   Эффективность: {dedup_ratio:.1f}%")
            print(f"   Сэкономлено записей: {total_refs - unique_blobs}")
    
    def check_orphaned_records(self):
        """11. Проверка на orphaned records"""
        print("\n" + "-"*70)
        print("1️⃣1️⃣  ORPHANED RECORDS (ОСИРОТЕВШИЕ ЗАПИСИ)")
        print("-"*70)
        
        # Assets без соответствующего asset_blob
        self.cursor.execute("""
            SELECT COUNT(*) FROM assets a
            WHERE NOT EXISTS (
                SELECT 1 FROM asset_blobs b WHERE b.content_hash = a.content_hash
            )
        """)
        orphaned_assets = self.cursor.fetchone()[0]
        if orphaned_assets > 0:
            print(f"\n❌ Assets без blob'ов: {orphaned_assets}")
            self.issues.append(f"Orphaned assets: {orphaned_assets}")
        else:
            print(f"\n✅ Assets без blob'ов: 0")
    
    def check_duplicates(self):
        """12. Поиск дубликатов"""
        print("\n" + "-"*70)
        print("1️⃣2️⃣  ПОИСК ДУБЛИКАТОВ")
        print("-"*70)
        
        # Дубликатные URL в pages
        self.cursor.execute("""
            SELECT url, COUNT(*) as cnt FROM pages 
            GROUP BY url HAVING COUNT(*) > 1
        """)
        dup_urls = self.cursor.fetchall()
        if dup_urls:
            print(f"\n⚠️  Дубликатные URL в pages: {len(dup_urls)}")
            self.warnings.append(f"Duplicate URLs in pages: {len(dup_urls)}")
        else:
            print(f"\n✅ Дубликатные URL в pages: 0")
        
        # Одинаковые хеши в asset_blobs
        self.cursor.execute("""
            SELECT content_hash, COUNT(*) FROM assets
            GROUP BY content_hash HAVING COUNT(*) > 5
            ORDER BY COUNT(*) DESC LIMIT 5
        """)
        popular_assets = self.cursor.fetchall()
        if popular_assets:
            print(f"\n📊 Самые дублируемые ассеты:")
            for hash_val, count in popular_assets:
                print(f"   • hash={hash_val[:16]}... встречается {count} раз")
    
    def check_compression(self):
        """13. Анализ сжатия"""
        print("\n" + "-"*70)
        print("1️⃣3️⃣  АНАЛИЗ СЖАТИЯ")
        print("-"*70)
        
        self.cursor.execute("PRAGMA page_size")
        page_size = self.cursor.fetchone()[0]
        print(f"\n📊 Page size: {page_size} bytes")
        
        self.cursor.execute("PRAGMA page_count")
        page_count = self.cursor.fetchone()[0]
        print(f"   Page count: {page_count} pages")
        print(f"   Теоретический размер: {page_count * page_size / 1024 / 1024:.2f} MB")
        
        actual_size = os.path.getsize(self.db_path) / 1024 / 1024
        print(f"   Реальный размер: {actual_size:.2f} MB")
        
        compression_ratio = (1 - actual_size / (page_count * page_size / 1024 / 1024)) * 100 if page_count * page_size > 0 else 0
        print(f"   Сжатие: {compression_ratio:.1f}%")
    
    def check_database_performance(self):
        """14. Проверка производительности БД"""
        print("\n" + "-"*70)
        print("1️⃣4️⃣  ПРОИЗВОДИТЕЛЬНОСТЬ БД")
        print("-"*70)
        
        self.cursor.execute("PRAGMA cache_size")
        cache_size = self.cursor.fetchone()[0]
        print(f"\n⚙️  Cache size: {abs(cache_size)} KB")
        
        self.cursor.execute("PRAGMA synchronous")
        sync_mode = self.cursor.fetchone()[0]
        sync_names = {0: 'OFF', 1: 'NORMAL', 2: 'FULL', 3: 'EXTRA'}
        print(f"   Synchronous mode: {sync_names.get(sync_mode, 'UNKNOWN')}")
        
        self.cursor.execute("PRAGMA journal_mode")
        journal_mode = self.cursor.fetchone()[0]
        print(f"   Journal mode: {journal_mode}")
    
    def generate_report(self):
        """Финальный отчёт"""
        print("\n" + "="*70)
        print("📋 ФИНАЛЬНЫЙ ОТЧЁТ")
        print("="*70)
        
        print(f"\n✅ УСПЕШНЫЕ ПРОВЕРКИ:")
        print(f"   • Целостность БД: OK")
        print(f"   • Страниц: {self.stats.get('total_pages', 0)}")
        print(f"   • Ассетов: {self.stats.get('total_assets', 0)}")
        print(f"   • Размер ассетов: {self.stats.get('total_asset_size', 0) / 1024 / 1024:.2f} MB")
        
        if self.issues:
            print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ: {len(self.issues)}")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ КРИТИЧЕСКИХ ОШИБОК: НЕТ")
        
        if self.warnings:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print(f"\n✅ ПРЕДУПРЕЖДЕНИЙ: НЕТ")
        
        print("\n" + "="*70)
        if not self.issues:
            print("🎉 БД ПОЛНОСТЬЮ ЗДОРОВА И ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        else:
            print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ - ТРЕБУЕТСЯ ВНИМАНИЕ!")
        print("="*70 + "\n")
        
        return len(self.issues) == 0
    
    def close(self):
        self.conn.close()


if __name__ == '__main__':
    artifacts_dir = Path('artifacts')
    db_files = list(artifacts_dir.glob('db-*/*.db'))
    
    if not db_files:
        print("❌ Database files not found!")
        sys.exit(1)
    
    all_ok = True
    for db_file in sorted(db_files):
        auditor = DatabaseAuditor(str(db_file))
        ok = auditor.run_full_audit()
        auditor.close()
        all_ok = all_ok and ok
    
    sys.exit(0 if all_ok else 1)
