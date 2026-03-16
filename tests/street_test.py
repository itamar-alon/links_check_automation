from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path 
import sys 
from sys import path 
import time
from datetime import datetime
import logging
import pytest

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from pages.street_page import StreetPage 

# שאיבת הלוגר המרכזי
logger = logging.getLogger("SystemFlowLogger")

def test_street_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    STREET_URL = secrets.get('street_url')
    if not STREET_URL:
        logger.error("❌ Error: Missing 'street_url' in secrets.json")
        pytest.fail("Missing 'street_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Street Info Test")
        
        street_page = StreetPage(driver, STREET_URL)
        street_page.open_street_page() 
        
        logger.info(">>> Waiting for main page elements to load...")
        wait = WebDriverWait(driver, 10)
        
        try:
            # 1. Attempt to locate search box (Best indicator page is working)
            search_box_locator = (By.XPATH, "//input | //*[contains(text(), 'שם הרחוב')]")
            wait.until(EC.presence_of_element_located(search_box_locator))
            logger.info("✅ Search component found on page.")
        except:
            # 2. If not found, check if redirected to login
            if "login" in driver.current_url.lower():
                raise Exception("❌ Redirected to Login page. Authentication might be required to view street info.")
            else:
                raise Exception("❌ Page loaded but Search field is missing. Content might be restricted.")

        # --- Step C: Run Data Verification Flow ---
        logger.info(">>> Starting street search and data verification...")
        street_page.search_and_verify_table() 
        
        logger.info(">>> Opening popup for extended data verification...")
        street_page.expand_and_verify_popup()
        
        logger.info("\n>>> Street Info page test finished successfully!") 
            
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