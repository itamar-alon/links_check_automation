import logging
import time
import os
from datetime import datetime
from urllib.parse import unquote
from playwright.sync_api import Page, expect
from .base_page import BasePage
from .login_page import LoginPage 

logger = logging.getLogger("SystemFlowLogger")

class EducationPage(BasePage):

    PAGE_TITLE_LOCATOR = "xpath=//h2[contains(normalize-space(.), 'רישום חינוך גני ילדים')]"
    CONTENT_VALIDATOR = "p:has-text('הנרטיב')"
    PRIVACY_GUARD_AUTH_BUTTON = "xpath=//button[contains(text(), 'המשך') or contains(text(), 'כניסה') or contains(text(), 'התחבר') or contains(text(), 'הזדהות')]"
    PRIVACY_GUARD_POPUP = ".MuiDialog-container" 
    LOGIN_IFRAME_TAG = "iframe"
    INTERNAL_TAB_ONLINE_FORMS = "button[role='tab']:has-text('טפסים מקוונים')"

    
    DEFAULT_TAB_LINKS = {
        "הילדים העירוניים": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=1",
        "והגשת ערעור": "https://www.edu-reg.co.il/closed?cid=8512834&sys=0&sub=2",
        "הגשת ערר": "https://www.edu-reg.co.il/closed?cid=8512834&sys=0&sub=2",
        "ביטול רישום": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=5",
        "נוסח מכתב הרשאה": "טופס ייפוי כח תשפו .pdf",
        "על כתובת מגורים": "תצהיר מגורים תשפו  .pdf",
        "תצהיר": "תצהיר הורים עצמאיים תשפו  .pdf",
        "הסכמה והתחייבות": "rishonlezion.muni.il/Residents/Education/registrationall/",
        "לגני הילדים": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=1", 
        "נספח": "נספח ד מונגש .pdf",
        "יצירת קשר": "rishonlezion.muni.il/Lists/List21/CustomDispForm"
    }

    ONLINE_FORMS_LINKS = {
        "יפוי כח": "טופס%20ייפוי%20כח%20תשפו%20.pdf", 
        "כתובת מגורים בעיר": "תצהיר%20מגורים%20תשפו%20%20.pdf",      
        "להורים": "תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf",
        "לימודי חוץ": "טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "נספח": "נספח%20ד%20מונגש%20.pdf" ,
        "בגן פרטי": "טופס%20בקשה%20להישארות%20שנה%20נוספת%20במעון%20.pdf" ,
        "הסכמה והתחייבות": "טופס%20הצהתשפו%20.pdf" ,
        "ויתור סודיות": "טופס%20ויתור%20סודיות%20.pdf" ,
        "ביטוח": "https://www.rishonlezion.muni.il/Activities/Pages/CityInsurance.aspx" ,
        "להוראת קבע באשראי": "ActiveDirectory?returnUrl=%2Fappbuilder%2Fformrender%3Fprocess%3DProcessHok141" 
    }

    TAB_3 = {
        "רישום לכיתה": "https://www.edu-reg.co.il/login" ,
        "שיבוץ והגשת וערר": "https://www.edu-reg.co.il/login" ,
        "שיבוץ והגשת ערר": "https://www.edu-reg.co.il/login" ,
        "ביטול רישום לבתי": "https://www.edu-reg.co.il/login" ,
        "נוסח מכתב הרשאה": "טופס%20ייפוי%20כח%20תשפו%20.pdf" ,
        "כתב הצהרה": "תצהיר%20מגורים%20תשפו%20%20.pdf" ,
        "תצהיר ל": "תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf" ,
        "בקשה לאישור לימודי": "טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=75" 
    }

    TAB_4 = {
        "תושבים חדשים": "https://www.edu-reg.co.il/login" ,
        "והגשת ערר": "https://www.edu-reg.co.il/login" ,
        "ביטול רישום לבתי": "https://www.edu-reg.co.il/login" ,
        "תצהיר מגורים": "תצהיר%20מגורים%20תשפו%20%20.pdf" ,
        "ויתור סודיות": "טופס%20ויתור%20סודיות%20.pdf" ,
        "תצהיר להורים": "תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf" ,
        "בקשה לאישור": "טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=76" 
    }

    TAB_5 = {
        "בתי ספר": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Schools.aspx" ,
        "גני ילדים": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Kindergardens.aspx" ,
        "ועדת זכאות": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Placement.aspx" ,
        "ועדת השגה": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/appeal.aspx" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=20" 
    }

    TAB_6 = {
        "תשלומי חינוך": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/29" ,
        "חינוך התראה": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/121" ,
        "תאונות אישיות": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/24" ,
        "בקשה להחזר": "https://tikshuv.rishonlezion.muni.il/hito/#/portal/main" ,
        "בקשת הצטרפות": "eFormRender.html" 
    }
    
    TAB_7 = {
        "גני": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=22" ,
        "חינוך יסודי": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=75" ,
        "על יסודי": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=76" ,
        "מיוחד": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=20" ,
        "ההסעות": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=85" 
    }

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.DEFAULT_TIMEOUT = 12000  # ms
        self.EDUCATION_URL = url

    def open_education_page(self):
        self.go_to_url(self.EDUCATION_URL)
        logger.info(f">>> Navigated to Education Interface: {self.EDUCATION_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE_LOCATOR).inner_text()

    def verify_education_content(self):
        logger.info("\n--- Starting Content Validation ---")
        try:
            self.page.locator(self.CONTENT_VALIDATOR).first.wait_for(state="visible", timeout=10000)
            logger.info("✅ Education page content verified!")
        except Exception:
            raise Exception("❌ Validation text 'הנרטיב' not found.")

    def run_default_tab_external_link_tests(self):
        logger.info("\n--- Running Default Tab External Links ---")
        self.verify_links_from_dictionary(self.DEFAULT_TAB_LINKS, "Default Tab")

    def verify_links_from_dictionary(self, links_dict, context_name="Unknown Tab"):
        logger.info(f"\n--- Running Link Tests for: {context_name} ---")
        if not links_dict:
            logger.warning(f"⚠️ Warning: No links defined for {context_name}.")
            return
        for text, url in links_dict.items():
            self._verify_external_link(text, url)

    def navigate_to_side_tab(self, tab_name):
        logger.info(f"\n--- Navigating to Side Tab: {tab_name} ---")
        
        if tab_name == "תיק תלמיד":
            self.page.reload()
            self.page.wait_for_load_state("networkidle")

        try:
            target_element = self.page.locator(f"text='{tab_name}' >> visible=true").first
            target_element.wait_for(state="visible", timeout=15000)
            target_element.scroll_into_view_if_needed()
            target_element.click()
            logger.info(f"✅ Successfully navigated to: {tab_name}")
            self.page.wait_for_load_state("domcontentloaded")
            return
        except Exception as e:
            raise Exception(f"❌ Failed to navigate to {tab_name}: {e}")

    def perform_student_login(self, user_id, user_password):
        logger.info(f"\n STARTING LOGIN FLOW via LoginPage")
        try:
            auth_btn = self.page.locator(self.PRIVACY_GUARD_AUTH_BUTTON)
            if auth_btn.is_visible(timeout=5000):
                auth_btn.click()
        except: pass
        
        self.page.wait_for_timeout(1000) 
        
        iframe_element = self.page.locator(self.LOGIN_IFRAME_TAG).first
        if iframe_element.count() > 0:
            frame = self.page.frame_locator(self.LOGIN_IFRAME_TAG).first
            try:
                login_page = LoginPage(self.page, self.EDUCATION_URL)
                login_page.login_with_password_inside_modal(user_id, user_password, frame=frame)
            except Exception as e:
                raise e
        
        try:
            popup = self.page.locator(self.PRIVACY_GUARD_POPUP)
            popup.wait_for(state="hidden", timeout=15000)
            logger.info("✅ Login successful! Modal closed.")
            self.page.wait_for_timeout(1500)
            return True
        except: return False

    def navigate_to_online_forms_after_login(self):
        logger.info("\n--- Navigating to Internal Tab: טפסים מקוונים ---")
        for attempt in range(2):
            try:
                self.page.wait_for_load_state("domcontentloaded")
                visible_tab = self.page.locator(f"{self.INTERNAL_TAB_ONLINE_FORMS} >> visible=true").first
                visible_tab.wait_for(state="visible", timeout=15000)
                visible_tab.scroll_into_view_if_needed()
                visible_tab.click()
                logger.info("✅ Clicked 'Online Forms' tab.")
                self.page.wait_for_load_state("networkidle")
                return True
            except Exception as e:
                if attempt == 0:
                    logger.warning(f"⚠️ First attempt to open 'Online Forms' failed, retrying after stabilization: {e}")
                    self.page.wait_for_timeout(1500)
                    continue
                logger.error(f"❌ Failed to click 'Online Forms' tab: {e}")
                return False

    def run_online_forms_link_tests(self):
        self.verify_links_from_dictionary(self.ONLINE_FORMS_LINKS, "Online Forms Internal")

    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_{safe_name}_{timestamp}.png"
            
            self.page.screenshot(path=filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        link_locator_str = f"//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{link_text}')]"
        try:
            locator = self.page.locator(link_locator_str).first
            locator.wait_for(state="attached", timeout=10000)
        except Exception:
            logger.error(f"❌ Link error: {link_text} (Element not found)")
            self._take_error_screenshot(link_text) 
            return

        href = locator.get_attribute("href")
        
        try:
            if href and "http" in href:
                decoded_href = unquote(href).strip()
                decoded_expected = unquote(expected_url_part).strip()
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed (HREF): {link_text}")
                    return
            
            with self.page.expect_popup() as popup_info:
                locator.scroll_into_view_if_needed()
                locator.click(force=True)
            
            new_page = popup_info.value
            new_page.wait_for_load_state()
            
            current_url = unquote(new_page.url).strip()
            expected_decoded = unquote(expected_url_part).strip()

            if expected_decoded in current_url:
                logger.info(f"✅ Passed: {link_text}")
            else:
                 logger.warning(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: {expected_decoded}\n   Actual: {current_url}")
            
            new_page.close()
        except Exception as e:
            logger.error(f"❌ Link error: {link_text} (Click failed or verification error: {e})")
            self._take_error_screenshot(link_text)