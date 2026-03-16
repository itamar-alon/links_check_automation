import sys
from pathlib import Path
from selenium import webdriver
import time
from datetime import datetime
import logging
import pytest

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pages.water_page import WaterPage

# שאיבת הלוגר המרכזי
logger = logging.getLogger("SystemFlowLogger")

def test_water_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    WATER_URL = secrets.get('water_url')
    if not WATER_URL:
        logger.error("❌ Error: Missing 'water_url' in secrets.json")
        pytest.fail("Missing 'water_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Water Interface Test")
        
        page = WaterPage(driver, WATER_URL)
        page.open_water_page()
        
        title = page.get_page_title()
        if "מים" in title or "Water" in title:
            logger.info(f"✅ Page Title: {title}")
        else:
            logger.warning(f"⚠️ Warning: Title might be different. Got: {title}")
        
        # --- טאב 1 ---
        page.run_tab_1_external_link_tests()
        
        # --- מעבר לטאב 2 וריצה ---
        page.navigate_to_tab_2()
        page.run_tab_2_external_link_tests()

        # --- מעבר לטאב 3 וריצה ---
        page.navigate_to_tab_3()
        page.run_tab_3_external_link_tests()
        
        logger.info("\n✅ Water Interface test finished successfully!")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"water_fail_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
        
        if driver:
            driver.save_screenshot(screenshot_path)
        
        logger.error(f"\n❌ CRITICAL FAILURE LOGGED")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        
        if driver:
            time.sleep(5)
        raise e