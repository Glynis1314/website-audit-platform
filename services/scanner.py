from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time


def scan_website(url):
    """
    Opens the website using Selenium,
    captures a screenshot,
    and returns the page information.
    """

    try:
        if not url.startswith("http"):
            url = "https://" + url

        os.makedirs("screenshots", exist_ok=True)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        driver.get(url)

        time.sleep(3)

        title = driver.title
        current_url = driver.current_url
        html = driver.page_source

        screenshot_path = os.path.join(
            "screenshots",
            "website.png"
        )

        driver.save_screenshot(
            screenshot_path
        )

        driver.quit()

        return {
            "success": True,
            "title": title,
            "url": current_url,
            "html": html,
            "screenshot": screenshot_path
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }