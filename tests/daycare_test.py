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

from tests.utils.secrets_loader import load_secrets
from pages.daycare_page import DaycarePage

# שאיבת הלוגר המרכזי שהגדרנו ב-conftest
logger = logging.getLogger("SystemFlowLogger")

# --- עטיפת הסקריפט בפונקציית טסט של Pytest וקבלת ה-fixtures ---
def test_daycare_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    DAYCARE_URL = secrets.get('daycare_url')
    if not DAYCARE_URL:
        logger.error("❌ Error: Missing 'daycare_url' in secrets.json")
        pytest.fail("Missing 'daycare_url' in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Daycare Test")
        
        # אתחול ופתיחת דף
        daycare_page = DaycarePage(driver, DAYCARE_URL)
        daycare_page.open_daycare_page()
        
        # --- Step B: Title Validation ---
        page_title = daycare_page.get_page_title()
        if "צהרונים" in page_title or "Daycare" in page_title:
             logger.info(f"✅ Page title verified: {page_title}")
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")
        
        # --- Step C: Run Link Tests (Tab 1 - צהרונים) ---
        daycare_page.run_tab_1_external_link_tests()
        
        # --- Step D: Run Link Tests (Tab 2 - מעונות יום) ---
        # מבצעים ניווט לטאב השני
        daycare_page.navigate_to_daycare_tab()
        # מריצים את בדיקת הקישורים של הטאב השני
        daycare_page.run_tab_2_external_link_tests()

        logger.info("\n>>> Daycare page test completed successfully!")
        
    except Exception as e:
        # טיפול בשגיאות קריטיות שגרמו לקריסת הטסט (כגון אלמנט לא נמצא בניווט לטאב)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"critical_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
        
        if driver: 
            driver.save_screenshot(screenshot_path)
        
        logger.error(f"\n❌ CRITICAL FAILURE LOGGED")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        
        # משאירים דפדפן פתוח לקצת זמן במקרה של שגיאה
        if driver:
            time.sleep(5)
        raise e