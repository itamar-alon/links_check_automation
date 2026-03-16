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

from pages.parking_page import ParkingPage

# שאיבת הלוגר המרכזי
logger = logging.getLogger("SystemFlowLogger")

def test_parking_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    PARKING_URL = secrets.get('parking_url')
    if not PARKING_URL:
        logger.error("❌ Error: Missing 'parking_url' in secrets.json")
        pytest.fail("Missing 'parking_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Parking Interface Test")
        
        # 1. פתיחת הדף
        parking_page = ParkingPage(driver, PARKING_URL)
        parking_page.open_parking_page()
        
        # 2. בדיקת כותרת
        page_title = parking_page.get_page_title()
        if "חניה" in page_title or "Parking" in page_title:
             logger.info(f"✅ Page title verified: {page_title}")
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")
        
        # 3. בדיקת קישורים - טאב 1 (דוחות חניה)
        parking_page.run_tab_1_external_link_tests()
        
        # 4. מעבר לטאב 3 (דילוג על טאב 2)
        parking_page.navigate_to_tab_3()
        
        # 5. בדיקת קישורים - טאב 3 (תווי חניה)
        parking_page.run_tab_3_external_link_tests()

        logger.info("\n>>> Parking Interface test finished successfully!")
        
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