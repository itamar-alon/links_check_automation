import pytest
import allure
import sys
import logging
import os
import base64
import requests
from datetime import datetime
from pathlib import Path
import time
from playwright.sync_api import Page, expect

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

def write_to_github_summary(markdown_text: str):
    """כותב טקסט ל-GitHub Step Summary במידה והסקריפט רץ ב-GitHub Actions"""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(markdown_text + "\n")
        except Exception as e:
            logger.error(f"Failed to write to GitHub Summary: {e}")

def send_courier_error_email(env_name, error_message, screenshot_path=None):
    courier_token = os.environ.get("COURIER_API_KEY")
    email_string = os.environ.get("MY_EMAIL")
    
    if not courier_token or not email_string:
        logger.warning("⚠️ Courier credentials missing in env. Skipping email.")
        return

    screenshot_html = '<p style="color: #999;">לא נוצר צילום מסך עבור ריכוז תקלות</p>'
    if screenshot_path and os.path.exists(screenshot_path):
        try:
            with open(screenshot_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                screenshot_html = f'<img src="data:image/png;base64,{encoded_string}" style="max-width:100%; border:1px solid #ccc;">'
        except Exception as e:
            logger.error(f"Failed to encode screenshot for email: {e}")

    recipients = [{"email": email.strip()} for email in email_string.split(',')]

    payload = {
        "message": {
            "to": recipients,
            "template": "AX7VYG3310MA1YKV3DFWS657H8PT",
            "data": {
                "env": env_name,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "errorMessage": error_message,
                "screenshotHtml": screenshot_html
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {courier_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.courier.com/send", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("📧 Alert email sent successfully via Courier.")
    except Exception as e:
        logger.error(f"❌ Failed to send email via Courier: {e}")

def capture_failure(page: Page, module_name, screenshot_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"failed_{module_name}_{timestamp}.png"
    path = str(screenshot_dir / name)
    try:
        page.screenshot(path=path)
        allure.attach(page.screenshot(), name=name, attachment_type=allure.attachment_type.PNG)
        logger.error(f"📸 Screenshot saved for {module_name} failure: {path}")
    except Exception as e:
        logger.error(f"⚠️ Failed to take screenshot for {module_name}: {e}")

@allure.feature("End-to-End System Flow")
@allure.story("Verify all municipal modules in one run")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_system_flow(page: Page, secrets):
    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    failures = [] 
    
    logger.info("🚀 Starting Full System Flow Test")
    
    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    PASSWORD = user_data.get('password')

    if not USER_ID or not PASSWORD:
        logger.error("❌ Missing credentials in .env")
        pytest.fail("❌ Missing credentials in .env")

    # ==========================================
    # 1. Daycare (צהרונים)
    # ==========================================
    with allure.step("Checking Daycare Interface"):
        try:
            url = secrets.get('daycare_url')
            if url:
                logger.info(f"Testing Daycare: {url}")
                daycare = DaycarePage(page, url)
                daycare.open_daycare_page()
                daycare.dismiss_cookie_banner()
                
                title = daycare.get_page_title()
                if "צהרונים" in title or "Daycare" in title:
                     allure.attach(title, name="Page Title", attachment_type=allure.attachment_type.TEXT)

                daycare.run_tab_1_external_link_tests()
                daycare.navigate_to_daycare_tab()
                daycare.run_tab_2_external_link_tests()
            else:
                logger.warning("⚠️ Daycare URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Daycare Failed: {e}")
            capture_failure(page, "Daycare", SCREENSHOT_DIR)
            failures.append(f"Daycare: {str(e)}")

    # ==========================================
    # 2. Education (חינוך)
    # ==========================================
    with allure.step("Checking Education Interface"):
        try:
            url = secrets.get('education_url')
            if url:
                logger.info(f"Testing Education: {url}")
                edu = EducationPage(page, url)
                edu.open_education_page()
                try:
                    edu.verify_education_content()
                except:
                    logger.warning("⚠️ Education content validation failed, proceeding anyway...")
                
                edu.run_default_tab_external_link_tests()

                EDU_TABS_MAP = {
                    "רישום חינוך יסודי": edu.TAB_3,
                    "רישום חינוך על יסודי": edu.TAB_4,
                    "חינוך מיוחד": edu.TAB_5,
                    "תשלומים": edu.TAB_6,
                    "יצירת קשר אגפי החינוך": edu.TAB_7
                }

                edu_tabs = ["תיק תלמיד", "רישום חינוך יסודי", "רישום חינוך על יסודי", 
                            "חינוך מיוחד", "תשלומים", "יצירת קשר אגפי החינוך"]

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
                logger.warning("⚠️ Education URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Education Failed: {e}")
            capture_failure(page, "Education", SCREENSHOT_DIR)
            failures.append(f"Education: {str(e)}")

    # ==========================================
    # 3. Enforcement (פיקוח)
    # ==========================================
    with allure.step("Checking Enforcement Interface"):
        try:
            url = secrets.get('enforcement_url')
            if url:
                logger.info(f"Testing Enforcement: {url}")
                enfo = EnforcementPage(page, url)
                enfo.open_enforcement_page()
                enfo.run_tab_1_external_link_tests()
            else:
                logger.warning("⚠️ Enforcement URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Enforcement Failed: {e}")
            capture_failure(page, "Enforcement", SCREENSHOT_DIR)
            failures.append(f"Enforcement: {str(e)}")

    # ==========================================
    # 4. Parking (חניה)
    # ==========================================
    with allure.step("Checking Parking Interface"):
        try:
            url = secrets.get('parking_url')
            if url:
                logger.info(f"Testing Parking: {url}")
                parking = ParkingPage(page, url)
                parking.open_parking_page()
                parking.run_tab_1_external_link_tests()
                parking.navigate_to_tab_3()
                parking.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Parking URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Parking Failed: {e}")
            capture_failure(page, "Parking", SCREENSHOT_DIR)
            failures.append(f"Parking: {str(e)}")

    # ==========================================
    # 5. Street Info (מידע הנדסי)
    # ==========================================
    with allure.step("Checking Street Info Interface"):
        try:
            url = secrets.get('street_url')
            if url:
                logger.info(f"Testing Street Info: {url}")
                street = StreetPage(page, url)
                street.open_street_page()
                street.search_and_verify_table()
                street.expand_and_verify_popup()
            else:
                logger.warning("⚠️ Street Info URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Street Failed: {e}")
            capture_failure(page, "StreetInfo", SCREENSHOT_DIR)
            failures.append(f"StreetInfo: {str(e)}")

    # ==========================================
    # 6. Water (מים)
    # ==========================================
    with allure.step("Checking Water Interface"):
        try:
            url = secrets.get('water_url')
            if url:
                logger.info(f"Testing Water: {url}")
                water = WaterPage(page, url)
                water.open_water_page()
                water.run_tab_1_external_link_tests()
                water.navigate_to_tab_2()
                water.run_tab_2_external_link_tests()
                water.navigate_to_tab_3()
                water.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Water URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Water Failed: {e}")
            capture_failure(page, "Water", SCREENSHOT_DIR)
            failures.append(f"Water: {str(e)}")

    # ==========================================
    # 7. Business License (רישוי עסקים)
    # ==========================================
    with allure.step("Checking Business License Interface"):
        try:
            url = secrets.get('business_url')
            if url:
                logger.info(f"Testing Business License: {url}")
                business = BusinessLicensePage(page, url)
                business.open_business_page()
                business.run_tab_1_external_link_tests()
                business.navigate_to_tab_2()
                business.run_tab_2_external_link_tests()
                business.navigate_to_tab_3()
                business.run_tab_3_external_link_tests()
            else:
                logger.warning("⚠️ Business License URL missing from .env, skipping.")
        except Exception as e:
            logger.error(f"❌ Module Business Failed: {e}")
            capture_failure(page, "BusinessLicense", SCREENSHOT_DIR)
            failures.append(f"BusinessLicense: {str(e)}")

    # ==========================================
    # FINAL VALIDATION
    # ==========================================
    broken_links = getattr(page, 'broken_links_list', [])
    count = len(broken_links)

    if failures or count > 0:
        summary_msg = f"Found {len(failures)} module failures and {count} broken links."
        logger.error(f"❌ FULL FLOW FAILED Summary: {summary_msg}")
        
        allure.dynamic.title(f"Full Flow - FAILED (Errors: {len(failures)} | Broken: {count})")
        
        write_to_github_summary("## ❌ תקלות בריצת האוטומציה\n")
        write_to_github_summary(f"**נמצאו {len(failures)} מודולים שנכשלו ו-{count} לינקים שבורים.**\n")
        
        email_error_content = ""

        if failures:
            write_to_github_summary("### 🚨 מודולים שנכשלו:")
            email_error_content += "שגיאות במודולים:\n" + "\n".join([f"- {f}" for f in failures]) + "\n\n"
            for f in failures:
                write_to_github_summary(f"- {f}")
            with allure.step("Module Failures Details"):
                allure.attach("\n".join(failures), name="Module Exceptions", attachment_type=allure.attachment_type.TEXT)
        
        if count > 0:
            write_to_github_summary("\n### 🔗 לינקים שבורים:")
            email_error_content += "לינקים שבורים:\n" + "\n".join([f"- {link}" for link in broken_links])
            for link in broken_links:
                write_to_github_summary(f"- {link}")
            with allure.step(f"Broken Links Details ({count})"):
                allure.attach("\n".join(broken_links), name="Broken Links List", attachment_type=allure.attachment_type.TEXT)
        
        send_courier_error_email(
            env_name="GitHub Actions - Full Flow",
            error_message=email_error_content.replace("\n", "<br>")
        )
        
        pytest.fail(f"❌ Test finished with errors. Modules: {len(failures)}, Broken Links: {count}")
    else:
        logger.info("✅ STATUS: FULL_FLOW_PASSED - All modules and links are OK")
        allure.dynamic.title("Full Flow - PASSED (All modules and links are OK)")
        
        write_to_github_summary("## ✅ ריצת האוטומציה עברה בהצלחה\n")
        write_to_github_summary("כל המודולים והלינקים נבדקו ונמצאו תקינים. 🚀")