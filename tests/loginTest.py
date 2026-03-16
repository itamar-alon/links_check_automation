from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import logging
import pytest
import time
from datetime import datetime
import sys

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pages.login_page import LoginPage

# Get the central logger
logger = logging.getLogger("SystemFlowLogger")

def test_login_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    USER_PASSWORD = user_data.get('password')
    LOGIN_URL = secrets.get('login_url')
    HOME_URL_PART = secrets.get('home_url_part')

    if not all([USER_ID, USER_PASSWORD, LOGIN_URL, HOME_URL_PART]):
        logger.error("❌ Error: Missing login configuration in secrets.json")
        pytest.fail("Missing login configuration in secrets.json")
        
    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Login Test")
        
        # Initialize the Page Object
        login_page = LoginPage(driver, LOGIN_URL)

        # Perform login
        login_page.login_with_password(USER_ID, USER_PASSWORD)

        # Wait for successful navigation
        login_page.wait_for_successful_login(HOME_URL_PART)

        logger.info("✅ Login confirmed successfully.")

    except TimeoutException as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"login_timeout_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
        
        if driver:
            driver.save_screenshot(screenshot_path)
        
        current_url = driver.current_url if driver else "N/A"
        logger.error(f"\n❌ LOGIN TEST FAILED (Timeout)")
        logger.error(f"Current URL: {current_url}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        
        if driver:
            time.sleep(5)
        raise e
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"login_critical_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
        
        if driver:
            driver.save_screenshot(screenshot_path)
            
        logger.error(f"\n❌ LOGIN TEST FAILED (Critical)")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        
        if driver:
            time.sleep(5)
        raise e