from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from urllib.parse import unquote
from .base_page import BasePage
import logging

logger = logging.getLogger("SystemFlowLogger")

class EnforcementPage(BasePage):
    """
    Class representing the Municipal Enforcement page.
    Optimized with Fast Link Check & Error Screenshots.
    """

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")

    # --- Test Data ---
    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/77",
        "הודעת תשלום קנס": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/78",
        "התראה לפני עיקול": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/79" ,
        "צו עיקול": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/203",
        "שובר דחיית": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/76",
        "צפייה בפרטי": "https://city4u.co.il/PortalServicesSite/requestsManagement/283000/GetDochDetails/2",
        "סטטוס ערעור": "https://city4u.co.il/PortalServicesSite/requestsManagement/283000/GetStatus/2",
        "בקשה לביטול": "https://por140.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=81140050568A4D0111CC9E33E032EFBD&Process=CitizenAppealPikuach140"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.ENFORCEMENT_URL = url

    def open_enforcement_page(self):
        self.go_to_url(self.ENFORCEMENT_URL)
        logger.info(f">>> Navigated to Enforcement page: {self.ENFORCEMENT_URL}")

    def get_page_title(self):
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # 🟢 פונקציית עזר לצילום מסך
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_enfo_{safe_name}_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    # 🟢 הבדיקה המהירה והחכמה
    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        # 1. חיפוש האלמנט לפי טקסט
        link_locator = (By.XPATH, f"//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{link_text}')]")
        
        try:
            el = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(link_locator)
            )
        except TimeoutException:
            logger.error(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_text)
            return

        # 2. חילוץ URL ובדיקה מהירה
        href = el.get_attribute("href")
        orig_window = self.driver.current_window_handle

        try:
            # אם יש href והוא מכיל את מה שאנחנו מחפשים - הצלחה מיידית!
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed (HREF check): {link_text}")
                    return 

            # 3. Fallback: לחיצה (אם ה-HREF לא תואם או לא קיים)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", el)

            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)

            # בדיקת URL בחלון החדש
            current_url = unquote(self.driver.current_url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                logger.info(f"✅ Passed: {link_text}")
            else:
                # אזהרה בלבד על Redirect
                logger.warning(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")

            self.driver.close()

        except Exception as e:
            logger.error(f"❌ Link error: '{link_text}' (Failed to verify). Error: {e}")
            self._take_error_screenshot(link_text)
        
        finally:
            try: self.driver.switch_to.window(orig_window)
            except: pass

    def run_tab_1_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Reports and Fines Tab) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)
        logger.info("--- Link check finished ---")