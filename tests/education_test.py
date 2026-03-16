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
from pages.education_page import EducationPage

# שאיבת הלוגר המרכזי
logger = logging.getLogger("SystemFlowLogger")

def test_education_flow(driver, secrets):
    # --- 2. Configuration ---
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    EDUCATION_URL = secrets.get('education_url')
    user_data = secrets.get('user_data', {})
    STUDENT_ID = user_data.get('id_number')
    STUDENT_PASS = user_data.get('password')

    if not all([EDUCATION_URL, STUDENT_ID, STUDENT_PASS]):
        logger.error("❌ Error: Missing 'education_url', 'id_number', or 'password' in secrets.")
        pytest.fail("Missing critical configuration in secrets.json")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # --- 3. Start Test ---
    try:
        logger.info("🚀 Starting Education Interface Test")
        
        education_page = EducationPage(driver, EDUCATION_URL)
        education_page.open_education_page()
        
        education_page.verify_education_content()
        education_page.run_default_tab_external_link_tests()

        # 🟢 מיפוי: איזה מילון מתאים לאיזה טאב
        TABS_DATA_MAP = {
            "רישום חינוך יסודי": education_page.TAB_3,
            "רישום חינוך על יסודי": education_page.TAB_4,
            "חינוך מיוחד": education_page.TAB_5,
            "תשלומים": education_page.TAB_6,
            "יצירת קשר": education_page.TAB_7
        }

        side_tabs = [
            "תיק תלמיד",
            "רישום חינוך יסודי",
            "רישום חינוך על יסודי",
            "חינוך מיוחד",
            "תשלומים",
            "יצירת קשר"
        ]
        
        for tab in side_tabs:
            education_page.navigate_to_side_tab(tab)

            # לוגיקה ייחודית לתיק תלמיד
            if tab == "תיק תלמיד":
                logger.info(f"🛑 Reached '{tab}' - Initiating Login...")
                success = education_page.perform_student_login(STUDENT_ID, STUDENT_PASS)
                if not success: 
                    raise Exception("Login Failed!")
                
                if education_page.navigate_to_online_forms_after_login():
                    education_page.run_online_forms_link_tests()
                continue

            # לוגיקה לשאר הטאבים
            if tab in TABS_DATA_MAP:
                links_dict = TABS_DATA_MAP[tab]
                education_page.verify_links_from_dictionary(links_dict, tab)
            else:
                logger.info(f"ℹ️ No links dictionary mapped for tab: {tab}")

        logger.info("\n>>> Education Interface test finished successfully!")
        
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