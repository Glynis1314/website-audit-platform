from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from utils.url_safety import is_safe_public_url

def scan_website(url):
    """
    Opens the website using Selenium,
    captures a screenshot,
    extracts W3C performance metrics,
    and returns the page information.
    """
    driver = None
    try:
        if not url.startswith("http"):
            url = "https://" + url

        is_safe, reason = is_safe_public_url(url)
        if not is_safe:
            return {"success": False, "error": reason}

        os.makedirs("screenshots", exist_ok=True)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        # Set page load timeout
        driver.set_page_load_timeout(20)
        driver.get(url)

        # Allow dynamic JS content to settle
        time.sleep(3)

        title = driver.title
        current_url = driver.current_url
        html = driver.page_source

        # Take screenshot
        import uuid
        unique_id = uuid.uuid4().hex
        screenshot_path = os.path.join(
            "screenshots",
            f"screenshot_{unique_id}.png"
        )
        driver.save_screenshot(screenshot_path)

        # Extract W3C Navigation Timing parameters
        performance_timings = driver.execute_script("""
            try {
                var t = window.performance.timing;
                if (!t) return null;
                return {
                    navigationStart: t.navigationStart || 0,
                    redirectStart: t.redirectStart || 0,
                    redirectEnd: t.redirectEnd || 0,
                    fetchStart: t.fetchStart || 0,
                    domainLookupStart: t.domainLookupStart || 0,
                    domainLookupEnd: t.domainLookupEnd || 0,
                    connectStart: t.connectStart || 0,
                    connectEnd: t.connectEnd || 0,
                    secureConnectionStart: t.secureConnectionStart || 0,
                    requestStart: t.requestStart || 0,
                    responseStart: t.responseStart || 0,
                    responseEnd: t.responseEnd || 0,
                    domLoading: t.domLoading || 0,
                    domInteractive: t.domInteractive || 0,
                    domContentLoadedEventStart: t.domContentLoadedEventStart || 0,
                    domContentLoadedEventEnd: t.domContentLoadedEventEnd || 0,
                    domComplete: t.domComplete || 0,
                    loadEventStart: t.loadEventStart || 0,
                    loadEventEnd: t.loadEventEnd || 0
                };
            } catch (e) {
                return null;
            }
        """)

        driver.quit()

        return {
            "success": True,
            "title": title,
            "url": current_url,
            "html": html,
            "screenshot": screenshot_path,
            "performance_timings": performance_timings
        }

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return {
            "success": False,
            "error": str(e)
        }