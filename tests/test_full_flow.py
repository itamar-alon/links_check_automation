import pytest
import allure
import sys
from pathlib import Path
from selenium import webdriver

# --- Path Fix (כמו בקובץ המקורי שלך) ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 
from pages.daycare_page import DaycarePage 
from pages.education_page import EducationPage
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage 
from pages.street_page import StreetPage
from pages.water_page import WaterPage
from pages.parking_page import ParkingPage

# --- Fixtures: הכנות לטסט ---

@pytest.fixture(scope="session")
def secrets():
    """טעינת הסודות פעם אחת לכל הריצה"""
    data = load_secrets()
    if not data:
        pytest.fail("❌ Error: Could not load secrets.json")
    return data

@pytest.fixture(scope="function")
def driver():
    """ניהול הדפדפן: פתיחה וסגירה אוטומטית"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    # יצירת מונה בתוך האובייקט של הדרייבר כדי שנוכל לגשת אליו מכל מקום
    driver.broken_links_list = [] 
    yield driver
    driver.quit() # יסגור את הדפדפן גם אם הטסט נכשל

# --- The Test ---

@allure.feature("End-to-End System Flow")
@allure.story("Verify all municipal modules in one run")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_system_flow(driver, secrets):
    
    # שליפת נתונים
    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    PASSWORD = user_data.get('password')

    if not USER_ID or not PASSWORD:
        pytest.fail("❌ Missing credentials in secrets.json")

    # ==========================================
    # 1. Daycare (צהרונים)
    # ==========================================
    with allure.step("Checking Daycare Interface"):
        url = secrets.get('daycare_url')
        print(f"Testing Daycare: {url}")
        
        daycare = DaycarePage(driver, url)
        daycare.open_daycare_page()
        
        title = daycare.get_page_title()
        if "צהרונים" in title or "Daycare" in title:
             allure.attach(title, name="Page Title", attachment_type=allure.attachment_type.TEXT)

        daycare.run_tab_1_external_link_tests()
        daycare.navigate_to_daycare_tab()
        daycare.run_tab_2_external_link_tests()

    # ==========================================
    # 2. Education (חינוך)
    # ==========================================
    with allure.step("Checking Education Interface"):
        url = secrets.get('education_url')
        edu = EducationPage(driver, url)
        edu.open_education_page()
        edu.verify_education_content()
        edu.run_default_tab_external_link_tests()

        # מיפוי טאבים
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
                edu.navigate_to_side_tab(tab)

                if tab == "תיק תלמיד":
                    if edu.perform_student_login(USER_ID, PASSWORD):
                        if edu.navigate_to_online_forms_after_login():
                            edu.run_online_forms_link_tests()
                    else:
                        allure.attach("Login Failed", name="Error", attachment_type=allure.attachment_type.TEXT)
                        # לא מכשיל את כל הטסט, רק מדלג
                        continue 

                if tab in EDU_TABS_MAP:
                    edu.verify_links_from_dictionary(EDU_TABS_MAP[tab], tab)

    # ==========================================
    # 3. Enforcement (פיקוח)
    # ==========================================
    with allure.step("Checking Enforcement Interface"):
        url = secrets.get('enforcement_url')
        enfo = EnforcementPage(driver, url)
        enfo.open_enforcement_page()
        enfo.run_tab_1_external_link_tests()

    # ==========================================
    # 4. Parking (חניה)
    # ==========================================
    with allure.step("Checking Parking Interface"):
        url = secrets.get('parking_url')
        parking = ParkingPage(driver, url)
        parking.open_parking_page()
        parking.run_tab_1_external_link_tests()
        parking.navigate_to_tab_3()
        parking.run_tab_3_external_link_tests()

    # ==========================================
    # 5. Street Info (מידע הנדסי)
    # ==========================================
    with allure.step("Checking Street Info Interface"):
        url = secrets.get('street_url')
        street = StreetPage(driver, url)
        street.open_street_page()
        street.search_and_verify_table()
        street.expand_and_verify_popup()

    # ==========================================
    # 6. Water (מים)
    # ==========================================
    with allure.step("Checking Water Interface"):
        url = secrets.get('water_url')
        if url:
            water = WaterPage(driver, url)
            water.open_water_page()
            water.run_tab_1_external_link_tests()
            water.navigate_to_tab_2()
            water.run_tab_2_external_link_tests()
            water.navigate_to_tab_3()
            water.run_tab_3_external_link_tests()

    # ==========================================
    # 7. Business License (רישוי עסקים)
    # ==========================================
    with allure.step("Checking Business License Interface"):
        url = secrets.get('business_url')
        if url:
            business = BusinessLicensePage(driver, url)
            business.open_business_page()
            business.run_tab_1_external_link_tests()
            business.navigate_to_tab_2()
            business.run_tab_2_external_link_tests()
            business.navigate_to_tab_3()
            business.run_tab_3_external_link_tests()

    # ==========================================
    # Allure Final Summary - הוספת סיכום הלינקים
    # ==========================================
    broken_links = getattr(driver, 'broken_links_list', [])
    count = len(broken_links)

    if count > 0:
        # שינוי שם הטסט בדוח כדי שיקפוץ לעין שיש בעיות
        allure.dynamic.title(f"Full Flow - PASSED (with {count} broken links)")
        with allure.step(f"🚨 Summary: Found {count} broken links"):
            allure.attach("\n".join(broken_links), name="List of Broken Links", attachment_type=allure.attachment_type.TEXT)
    else:
        allure.dynamic.title("Full Flow - PASSED (All links are OK)")