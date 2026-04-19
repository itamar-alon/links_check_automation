from pathlib import Path
import sys
from sys import path
from selenium import webdriver
import time
from datetime import datetime
import logging
import pytest

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets
from pages.business_page import BusinessLicensePage

logger = logging.getLogger("SystemFlowLogger")

def test_business_license_flow(driver, secrets):

    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    BUSINESS_URL = secrets.get('business_url')
    if not BUSINESS_URL:
        logger.error("❌ Error: Missing 'business_url' in secrets.json")
        pytest.fail("Missing 'business_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Business License Test")
        

        page = BusinessLicensePage(driver, BUSINESS_URL)
        page.open_business_page()
        
        title = page.get_page_title()
        logger.info(f"✅ Page Title: {title}")
        

        page.run_tab_1_external_link_tests()
        
        page.navigate_to_tab_2()
        page.run_tab_2_external_link_tests()

        page.navigate_to_tab_3()
        page.run_tab_3_external_link_tests()

        logger.info("\n>>> Business License test finished successfully!")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"critical_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
        
        if driver: 
            driver.save_screenshot(screenshot_path)
        
        logger.error(f"\n❌ CRITICAL FAILURE LOGGED")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        
        if driver:
            time.sleep(5)
        raise e