import pytest
import allure
import sys
import logging
from datetime import datetime
from pathlib import Path
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pages.daycare_page import DaycarePage 
from pages.education_page import EducationPage
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage 
from pages.street_page import StreetPage
from pages.water_page import WaterPage
from pages.parking_page import ParkingPage

logger = logging.getLogger("SystemFlowLogger")

def capture_failure(driver, module_name, screenshot_dir):
    """Helper to capture screenshot and attach to allure on local failure"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"failed_{module_name}_{timestamp}.png"
    path = str(screenshot_dir / name)
    try:
        driver.save_screenshot(path)
        allure.attach(driver.get_screenshot_as_png(), name=name, attachment_type=allure.attachment_type.PNG)
        logger.error(f"📸 Screenshot saved for {module_name} failure: {path}")
    except Exception as e:
        logger.error(f"⚠️ Failed to take screenshot for {module_name}: {e}")

@allure.feature("End-to-End System Flow")
@allure.story("Verify all municipal modules in one run")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_system_flow(driver, secrets):
    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    failures = [] 
    
    logger.info("🚀 Starting Full System Flow Test")
    
    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    PASSWORD = user_data.get('password')

    if not USER_ID or not PASSWORD:
        logger.error("❌ Missing credentials in secrets.json")
        pytest.fail("❌ Missing credentials in secrets.json")

    # ==========================================
    # 1. Daycare (צהרונים)
    # ==========================================
    with allure.step("Checking Daycare Interface"):
        try:
            url = secrets.get('daycare_url')
            if url:
                logger.info(f"Testing Daycare: {url}")
                daycare = DaycarePage(driver, url)
                daycare.open_daycare_page()
                daycare.dismiss_cookie_banner()
                
                title = daycare.get_page_title()
                if "צהרונים" in title or "Daycare" in title:
                     allure.attach(title, name="Page Title", attachment_type=allure.attachment_type.TEXT)

                daycare.run_tab_1_external_link_tests()
                daycare.navigate_to_daycare_tab()
                daycare.run_tab_2_external_link_tests()
            else:
                logger.warning("⚠️ Daycare URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Daycare Failed: {e}")
            capture_failure(driver, "Daycare", SCREENSHOT_DIR)
            failures.append(f"Daycare: {str(e)}")

    # ==========================================
    # 2. Education (חינוך)
    # ==========================================
    with allure.step("Checking Education Interface"):
        try:
            url = secrets.get('education_url')
            if url:
                logger.info(f"Testing Education: {url}")
                edu = EducationPage(driver, url)
                edu.open_education_page()
                edu.verify_education_content()
                edu.run_default_tab_external_link_tests()

                EDU_TABS_MAP = {
                    "רישום חינוך יסודי": edu.TAB_3,
                    "רישום חינוך על יסודי": edu.TAB_4,
                    "חינוך מיוחד": edu.TAB_5,
                    "תשלומים": edu.TAB_6,
                    "יצירת קשר": edu.TAB_7
                }

                edu_tabs = ["תיק תלמיד", "רישום חינוך יסודי", "רישום חינוך על יסודי", 
                            "חינוך מיוחד", "תשלומים", "יצירת קשר"]

                for tab in edu_tabs:
                    with allure.step(f"Education Tab: {tab}"):
                        logger.info(f"Navigating to Education Tab: {tab}")
                        edu.navigate_to_side_tab(tab)

                        if tab == "תיק תלמיד":
                            if edu.perform_student_login(USER_ID, PASSWORD):
                                if edu.navigate_to_online_forms_after_login():
                                    edu.run_online_forms_link_tests()
                            else:
                                logger.warning("⚠️ Student Login Failed. Skipping tab.")
                                allure.attach("Login Failed", name="Error", attachment_type=allure.attachment_type.TEXT)
                                continue 

                        if tab in EDU_TABS_MAP:
                            edu.verify_links_from_dictionary(EDU_TABS_MAP[tab], tab)
            else:
                logger.warning("⚠️ Education URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Education Failed: {e}")
            capture_failure(driver, "Education", SCREENSHOT_DIR)
            failures.append(f"Education: {str(e)}")

    # ==========================================
    # 3. Enforcement (פיקוח)
    # ==========================================
    with allure.step("Checking Enforcement Interface"):
        try:
            url = secrets.get('enforcement_url')
            if url:
                logger.info(f"Testing Enforcement: {url}")
                enfo = EnforcementPage(driver, url)
                enfo.open_enforcement_page()
                enfo.run_tab_1_external_link_tests()
            else:
                logger.warning("⚠️ Enforcement URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Enforcement Failed: {e}")
            capture_failure(driver, "Enforcement", SCREENSHOT_DIR)
            failures.append(f"Enforcement: {str(e)}")

    # ==========================================
    # 4. Parking (חניה)
    # ==========================================
    with allure.step("Checking Parking Interface"):
        try:
            url = secrets.get('parking_url')
            if url:
                logger.info(f"Testing Parking: {url}")
                parking = ParkingPage(driver, url)
                parking.open_parking_page()
                parking.run_tab_1_external_link_tests()
                parking.navigate_to_tab_3()
                parking.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Parking URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Parking Failed: {e}")
            capture_failure(driver, "Parking", SCREENSHOT_DIR)
            failures.append(f"Parking: {str(e)}")

    # ==========================================
    # 5. Street Info (מידע הנדסי)
    # ==========================================
    with allure.step("Checking Street Info Interface"):
        try:
            url = secrets.get('street_url')
            if url:
                logger.info(f"Testing Street Info: {url}")
                street = StreetPage(driver, url)
                street.open_street_page()
                street.search_and_verify_table()
                street.expand_and_verify_popup()
            else:
                logger.warning("⚠️ Street Info URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Street Failed: {e}")
            capture_failure(driver, "StreetInfo", SCREENSHOT_DIR)
            failures.append(f"StreetInfo: {str(e)}")

    # ==========================================
    # 6. Water (מים)
    # ==========================================
    with allure.step("Checking Water Interface"):
        try:
            url = secrets.get('water_url')
            if url:
                logger.info(f"Testing Water: {url}")
                water = WaterPage(driver, url)
                water.open_water_page()
                water.run_tab_1_external_link_tests()
                water.navigate_to_tab_2()
                water.run_tab_2_external_link_tests()
                water.navigate_to_tab_3()
                water.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Water URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Water Failed: {e}")
            capture_failure(driver, "Water", SCREENSHOT_DIR)
            failures.append(f"Water: {str(e)}")

    # ==========================================
    # 7. Business License (רישוי עסקים)
    # ==========================================
    with allure.step("Checking Business License Interface"):
        try:
            url = secrets.get('business_url')
            if url:
                logger.info(f"Testing Business License: {url}")
                business = BusinessLicensePage(driver, url)
                business.open_business_page()
                business.run_tab_1_external_link_tests()
                business.navigate_to_tab_2()
                business.run_tab_2_external_link_tests()
                business.navigate_to_tab_3()
                business.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Business License URL missing from secrets, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Business Failed: {e}")
            capture_failure(driver, "BusinessLicense", SCREENSHOT_DIR)
            failures.append(f"BusinessLicense: {str(e)}")

    # ==========================================
    # FINAL VALIDATION
    # ==========================================
    broken_links = getattr(driver, 'broken_links_list', []) if driver else []
    count = len(broken_links)

    if failures or count > 0:
        summary_msg = f"Found {len(failures)} module failures and {count} broken links."
        logger.error(f"❌ FULL FLOW FAILED Summary: {summary_msg}")
        
        allure.dynamic.title(f"Full Flow - FAILED (Errors: {len(failures)} | Broken: {count})")
        
        if failures:
            with allure.step("Module Failures Details"):
                allure.attach("\n".join(failures), name="Module Exceptions", attachment_type=allure.attachment_type.TEXT)
        
        if count > 0:
            with allure.step(f"Broken Links Details ({count})"):
                allure.attach("\n".join(broken_links), name="Broken Links List", attachment_type=allure.attachment_type.TEXT)
        
        pytest.fail(f"❌ Test finished with errors. Modules: {len(failures)}, Broken Links: {count}")
    else:
        logger.info("✅ STATUS: FULL_FLOW_PASSED - All modules and links are OK")
        allure.dynamic.title("Full Flow - PASSED (All modules and links are OK)")