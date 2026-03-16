from pathlib import Path
import sys
from sys import path
from selenium import webdriver
import time
from datetime import datetime
import logging
import pytest

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from pages.enfo_page import EnforcementPage 

# שאיבת הלוגר המרכזי
logger = logging.getLogger("SystemFlowLogger")

def test_enforcement_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    ENFORCEMENT_URL = secrets.get('enforcement_url')
    if not ENFORCEMENT_URL:
        logger.error("❌ Error: Missing 'enforcement_url' in secrets.json")
        pytest.fail("Missing 'enforcement_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Enforcement Interface Test")
        
        # --- Step A: Setup Page ---
        enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL) 
        enforcement_page.open_enforcement_page() 
        
        # --- Step B: Title Validation ---
        page_title = enforcement_page.get_page_title()
        if "פיקוח" in page_title or "Enforcement" in page_title:
             logger.info(f"✅ Page title verified: {page_title}") 
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")

        # --- Step C: Run Fast Link Tests ---
        enforcement_page.run_tab_1_external_link_tests() 
        
        logger.info("\n>>> Enforcement page test finished successfully!") 
        
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