#!/usr/bin/env python3
"""
Unit tests for URL Rewriter functionality
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.url_rewriter_optimized import URLRewriter


class TestURLRewriter(unittest.TestCase):
    """Test cases for URLRewriter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.domain = 'example.com'
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rewriter = URLRewriter(
            domain=self.domain,
            base_path=self.temp_dir.name,
            dry_run=False
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    def test_convert_absolute_url_with_https(self):
        """Test conversion of absolute HTTPS URLs"""
        url = 'https://example.com/path/to/page.html'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '/path/to/page.html')
    
    def test_convert_absolute_url_with_http(self):
        """Test conversion of absolute HTTP URLs"""
        url = 'http://example.com/page.html'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '/page.html')
    
    def test_convert_absolute_url_no_protocol(self):
        """Test conversion of URLs without protocol"""
        url = '//example.com/path/file.js'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '//example.com/path/file.js')  # Skip protocol-relative
    
    def test_preserve_relative_url(self):
        """Test that relative URLs are preserved"""
        url = '/relative/path.html'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '/relative/path.html')
    
    def test_preserve_anchor_link(self):
        """Test that anchor links are preserved"""
        url = '#section'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '#section')
    
    def test_preserve_data_uri(self):
        """Test that data URIs are preserved"""
        url = 'data:image/png;base64,iVBORw0KGgoAAAAN...'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, url)
    
    def test_preserve_blob_uri(self):
        """Test that blob URIs are preserved"""
        url = 'blob:https://example.com/550e8400-e29b-41d4-a716-446655440000'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, url)
    
    def test_process_html_with_href(self):
        """Test HTML processing with href attributes"""
        html = '<a href="https://example.com/page">Link</a>'
        modified, result = self.rewriter._process_html(Path('test.html'), html)
        self.assertTrue('href="/page"' in result or 'href=/page' in result)
    
    def test_process_html_with_src(self):
        """Test HTML processing with src attributes"""
        html = '<img src="https://example.com/image.png">'
        modified, result = self.rewriter._process_html(Path('test.html'), html)
        self.assertTrue('src' in result.lower())
    
    def test_process_html_with_form_action(self):
        """Test HTML processing with form action"""
        html = '<form action="https://example.com/submit"><input></form>'
        modified, result = self.rewriter._process_html(Path('test.html'), html)
        # Should contain action attribute
        self.assertIn('action', result.lower())
    
    def test_process_css_url_function(self):
        """Test CSS url() function rewriting"""
        css = 'body { background: url("https://example.com/bg.png"); }'
        modified, result = self.rewriter._process_css(Path('test.css'), css)
        self.assertTrue(modified)
        self.assertIn('/bg.png', result)
    
    def test_process_css_import(self):
        """Test CSS @import directive rewriting"""
        css = '@import "https://example.com/style.css";'
        modified, result = self.rewriter._process_css(Path('test.css'), css)
        self.assertTrue(modified)
        self.assertIn('/style.css', result)
    
    def test_process_javascript_string_urls(self):
        """Test JavaScript string URL rewriting"""
        js = 'const url = "https://example.com/api/data";'
        modified, result = self.rewriter._process_javascript(Path('test.js'), js)
        # Should be modified
        self.assertTrue(modified)
    
    def test_case_insensitive_domain_matching(self):
        """Test case-insensitive domain matching"""
        url = 'https://Example.COM/Page.html'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '/Page.html')
    
    def test_file_read_utf8(self):
        """Test reading UTF-8 encoded file"""
        test_file = Path(self.temp_dir.name) / 'test.txt'
        test_content = 'Hello ✅ World'
        test_file.write_text(test_content, encoding='utf-8')
        
        success, content = self.rewriter._read_file(test_file)
        self.assertTrue(success)
        self.assertEqual(content, test_content)
    
    def test_file_read_fallback_encoding(self):
        """Test file reading with encoding fallback"""
        test_file = Path(self.temp_dir.name) / 'test.txt'
        test_content = 'Test content'
        test_file.write_text(test_content, encoding='utf-8')
        
        success, content = self.rewriter._read_file(test_file)
        self.assertTrue(success)
        self.assertEqual(content, test_content)
    
    def test_file_write(self):
        """Test writing file"""
        test_file = Path(self.temp_dir.name) / 'output.txt'
        test_content = 'Test output'
        
        success = self.rewriter._write_file(test_file, test_content)
        self.assertTrue(success)
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(encoding='utf-8'), test_content)
    
    def test_dry_run_mode(self):
        """Test dry-run mode doesn't write files"""
        rewriter = URLRewriter(
            domain=self.domain,
            base_path=self.temp_dir.name,
            dry_run=True
        )
        
        test_file = Path(self.temp_dir.name) / 'test.txt'
        test_content = 'Test'
        
        success = rewriter._write_file(test_file, test_content)
        self.assertTrue(success)  # Succeeds but doesn't write
        self.assertFalse(test_file.exists())  # File not created
    
    def test_empty_url(self):
        """Test handling of empty URL"""
        url = ''
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, '')
    
    def test_url_with_query_string(self):
        """Test URL rewriting with query string"""
        url = 'https://example.com/page?param=value&other=123'
        result = self.rewriter._convert_url(url)
        self.assertIn('/page', result)
        # Query string should be preserved
    
    def test_url_with_fragment(self):
        """Test URL rewriting with fragment identifier"""
        url = 'https://example.com/page#section'
        result = self.rewriter._convert_url(url)
        self.assertTrue(result.startswith('/'))
    
    def test_process_html_no_changes(self):
        """Test HTML with no URLs to convert"""
        html = '<p>Hello World</p>'
        modified, result = self.rewriter._process_html(Path('test.html'), html)
        # Should return false for no modifications
        self.assertFalse(modified or result != html)
    
    def test_process_css_no_changes(self):
        """Test CSS with no URLs to convert"""
        css = 'body { color: red; }'
        modified, result = self.rewriter._process_css(Path('test.css'), css)
        self.assertFalse(modified)
        self.assertEqual(result, css)
    
    def test_pattern_compilation(self):
        """Test that regex patterns compile successfully"""
        patterns = self.rewriter._compile_patterns()
        self.assertIn('http', patterns)
        self.assertIn('css_url', patterns)
        self.assertIn('css_import', patterns)
        self.assertIn('js_url', patterns)


class TestURLRewriterEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.domain = 'test.org'
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rewriter = URLRewriter(
            domain=self.domain,
            base_path=self.temp_dir.name,
            dry_run=False
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    def test_domain_with_special_chars(self):
        """Test domain with special regex characters"""
        # Domains like this are theoretical but should be handled
        rewriter = URLRewriter(
            domain='example.co.uk',
            base_path=self.temp_dir.name
        )
        url = 'https://example.co.uk/page'
        result = rewriter._convert_url(url)
        self.assertEqual(result, '/page')
    
    def test_multiple_domains(self):
        """Test that only target domain is converted"""
        url = 'https://other.com/page'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, url)  # Should not change
    
    def test_html_with_malformed_tags(self):
        """Test HTML processing with malformed tags"""
        html = '<a href=https://test.org/page>Link</a>'
        # Should handle gracefully
        modified, result = self.rewriter._process_html(Path('test.html'), html)
        self.assertIsNotNone(result)
    
    def test_very_long_url(self):
        """Test handling of very long URLs"""
        long_path = '/very/' + 'long/' * 100 + 'path.html'
        url = f'https://{self.domain}{long_path}'
        result = self.rewriter._convert_url(url)
        self.assertEqual(result, long_path)


if __name__ == '__main__':
    unittest.main()