import unittest
import os
import json
import sqlite3
from services.seo import analyze_seo
from services.security import analyze_security, check_ssl_expiry
from services.performance import analyze_performance
from services.links import audit_links
import utils.db as db

class TestSiteVerifyAuditModules(unittest.TestCase):
    
    def setUp(self):
        # Sample HTML representing typical webpage structures
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="A simple test meta description that satisfies character limits.">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="canonical" href="https://example.com/test-page">
            <meta property="og:title" content="Open Graph Title">
            <meta property="og:image" content="https://example.com/image.png">
            <meta name="twitter:card" content="summary_large_image">
            <link rel="stylesheet" href="style.css">
            <style>body { background: #fff; }</style>
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
            <img src="logo.png" alt="Company Logo">
            <img src="banner.png"> <!-- Missing Alt -->
            
            <form action="https://example.com/login" method="post">
                <input type="email" name="email" id="email_field">
                <label for="email_field">Email Address</label>
                <input type="password" name="password" autocomplete="on">
                <button type="submit">Login</button>
            </form>
            
            <a href="/relative-path">Relative Link</a>
            <a href="https://example.com/about">Absolute Link</a>
            <a href="https://broken-link-example.org">Broken Link</a>
        </body>
        </html>
        """

    def test_seo_analysis(self):
        result = analyze_seo(self.sample_html)
        
        # Verify keys
        self.assertIn("seo_score", result)
        self.assertIn("seo_rating", result)
        self.assertIn("findings", result)
        
        # Check extraction
        self.assertEqual(result["title"], "Test Page Title")
        self.assertEqual(result["meta_description"], "A simple test meta description that satisfies character limits.")
        self.assertTrue(result["has_viewport"])
        self.assertTrue(result["has_canonical"])
        self.assertEqual(result["h1_count"], 1)
        self.assertEqual(result["h2_count"], 1)
        
        # Alt tags verification
        self.assertEqual(result["total_images"], 2)
        self.assertEqual(result["images_missing_alt"], 1)

    def test_security_analysis(self):
        # Run test with mock URL
        result = analyze_security(self.sample_html, "https://example.com")
        
        self.assertIn("security_score", result)
        self.assertIn("security_level", result)
        self.assertTrue(result["https"])
        self.assertEqual(result["password_fields"], 1)
        
        # Autocomplete was 'on', should identify it
        self.assertEqual(result["autocomplete_enabled"], 1)

    def test_performance_analysis(self):
        # Mock timing metrics
        timing_data = {
            "navigationStart": 1000,
            "domainLookupStart": 1010,
            "domainLookupEnd": 1030,
            "connectStart": 1035,
            "connectEnd": 1055,
            "requestStart": 1060,
            "responseStart": 1080,
            "responseEnd": 1100,
            "domLoading": 1110,
            "domComplete": 1200,
            "loadEventEnd": 1220
        }
        
        result = analyze_performance(self.sample_html, timing_data)
        
        self.assertIn("performance_score", result)
        self.assertEqual(result["images"], 2)
        self.assertEqual(result["scripts"], 0)
        self.assertEqual(result["stylesheets"], 1)
        self.assertEqual(result["inline_css"], 1)
        
        # Timing checks (in ms)
        metrics = result["metrics"]
        self.assertEqual(metrics["dns_lookup_ms"], 20)
        self.assertEqual(metrics["tcp_handshake_ms"], 20)
        self.assertEqual(metrics["ttfb_ms"], 20)
        self.assertEqual(metrics["page_load_ms"], 220)

    def test_link_auditor_extraction(self):
        result = audit_links(self.sample_html, "https://example.com")
        self.assertIn("total_links_found", result)
        
        # Should extract relative as absolute and absolute links (2 valid unique links)
        # Excludes duplicates or fragments if any
        self.assertGreaterEqual(result["total_links_found"], 2)

    def test_accessibility_analysis(self):
        from services.accessibility import analyze_accessibility
        
        html = """
        <html>
        <head><title>Accessibility Test</title></head>
        <body>
            <input type="text" id="username">
            <label for="username">Username</label>
            
            <input type="text" aria-label="Search site">
            
            <input type="text" id="labeled-by-el" aria-labelledby="label-id">
            <span id="label-id">Actual Label</span>
            
            <input type="text" id="unlabeled-1">
            <input type="text">
            
            <button></button> <!-- Empty button -->
            <button>Click</button>
        </body>
        </html>
        """
        result = analyze_accessibility(html)
        self.assertEqual(result["unlabeled_inputs"], 2) # unlabeled-1 and the one with no ID/attribute
        self.assertEqual(result["empty_buttons"], 1)
        self.assertEqual(result["missing_alt"], 0)


class TestDatabaseOperations(unittest.TestCase):
    
    def setUp(self):
        # Override DB_PATH to use a test DB file
        db.DB_PATH = "siteverify_test.db"
        db.init_db()

    def tearDown(self):
        # Remove the test database file
        if os.path.exists("siteverify_test.db"):
            try:
                os.remove("siteverify_test.db")
            except PermissionError:
                pass

    def test_save_and_retrieve_scan(self):
        report_data = {
            "website": {"title": "Test Site", "url": "https://example.com", "screenshot": "screenshots/website.png"},
            "overall_score": 92.5,
            "grade": "A",
            "status": "Excellent",
            "findings": ["Looks great!"]
        }
        
        # Save scan
        scan_id = db.save_scan(
            url="https://example.com",
            title="Test Site",
            overall_score=92.5,
            grade="A",
            status="Excellent",
            screenshot_path="screenshots/website.png",
            report_dict=report_data
        )
        
        self.assertIsNotNone(scan_id)
        
        # Fetch scan details
        scan = db.get_scan_by_id(scan_id)
        self.assertIsNotNone(scan)
        self.assertEqual(scan["url"], "https://example.com")
        self.assertEqual(scan["title"], "Test Site")
        self.assertEqual(scan["overall_score"], 92.5)
        self.assertEqual(scan["report"]["grade"], "A")
        
        # Check history
        history = db.get_scan_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["url"], "https://example.com")
        
        # Check aggregate stats
        stats = db.get_aggregate_stats()
        self.assertEqual(stats["total_scans"], 1)
        self.assertEqual(stats["avg_score"], 92.5)
        self.assertEqual(stats["highest_score"], 92.5)
        
        # Delete scan
        db.delete_scan(scan_id)
        scan_deleted = db.get_scan_by_id(scan_id)
        self.assertIsNone(scan_deleted)

class TestUrlSafety(unittest.TestCase):
    
    def test_safe_public_url(self):
        from utils.url_safety import is_safe_public_url
        
        # Test normal public URL passes
        is_safe, reason = is_safe_public_url("https://example.com")
        self.assertTrue(is_safe, f"Safe URL failed validation: {reason}")
        
        # Test explicit standard port combinations pass
        is_safe, reason = is_safe_public_url("http://example.com:80")
        self.assertTrue(is_safe, f"Standard HTTP port failed validation: {reason}")
        
        is_safe, reason = is_safe_public_url("https://example.com:443")
        self.assertTrue(is_safe, f"Standard HTTPS port failed validation: {reason}")

    def test_unsafe_local_and_private_urls(self):
        from utils.url_safety import is_safe_public_url
        
        # Loopback
        self.assertFalse(is_safe_public_url("http://127.0.0.1")[0])
        self.assertFalse(is_safe_public_url("http://localhost")[0])
        self.assertFalse(is_safe_public_url("http://[::1]")[0])
        
        # Cloud metadata
        self.assertFalse(is_safe_public_url("http://169.254.169.254")[0])
        self.assertFalse(is_safe_public_url("http://[fd00:ec2::254]")[0])
        
        # Private IPs
        self.assertFalse(is_safe_public_url("http://10.0.0.5")[0])
        self.assertFalse(is_safe_public_url("http://192.168.1.1")[0])
        self.assertFalse(is_safe_public_url("http://172.16.5.5")[0])

    def test_unsafe_ports(self):
        from utils.url_safety import is_safe_public_url
        
        # Non-standard ports
        self.assertFalse(is_safe_public_url("http://example.com:8080")[0])
        self.assertFalse(is_safe_public_url("https://example.com:8443")[0])
        self.assertFalse(is_safe_public_url("http://example.com:6379")[0])

    def test_dns_resolution_failure(self):
        from utils.url_safety import is_safe_public_url
        
        # Non-existent hostname
        is_safe, reason = is_safe_public_url("http://this-domain-does-not-exist-at-all-siteverify-test.com")
        self.assertFalse(is_safe)
        self.assertIn("DNS resolution failed", reason)

if __name__ == "__main__":
    unittest.main()
