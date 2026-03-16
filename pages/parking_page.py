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

class ParkingPage(BasePage):
    """
    Parking Page Object.
    Optimized for FAST link checking + Error Screenshots.
    Skips Login and Personal Info Tab as requested.
    """

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    # לוקייטור לטאב "תווי חניה"
    TAB_3_LOCATOR = (By.XPATH, "//button[contains(text(), 'תווי חניה')]")
    
    # לוקייטור גנרי לקישורים
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"

    # --- Data Dictionaries ---
    
    # טאב 1: דו"חות חניה (ברירת מחדל)
    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/4",
        "הודעת תשלום קנס": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/16",
        "התראה לפני עיקול": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/3",
        "צו עיקול מטלטלין": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/98",
        "שובר דחיית ערעור": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/36"
    }

    # טאב 3: תווי חניה
    TAB_3_EXTERNAL_LINKS = {
        "רשימת אזורי חניה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/LocalParkingTicketArea.aspx?prm=920082-1&language=he",
        "פירוט חניונים": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/Cityparking.aspx?prm=920082-1&language=he",
        "חידוש תו חניה": "https://mileon-portal.co.il/DynamicForm/resNew.aspx?prm=920082-1&language=he",
        "בדיקת תוקף": "https://mileon-portal.co.il/DynamicForm/ValidationLabelsNew.aspx?prm=920082-1&language=he",
        "השלמת מסמכים": "https://mileon-portal.co.il/DynamicForm/CompletingDocuments.aspx?prm=920082-1&language=he",
        "הקצאת חניה שמורה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/DisabledParking.aspx"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.PARKING_URL = url

    def open_parking_page(self):
        self.go_to_url(self.PARKING_URL)
        logger.info(f">>> Navigated to Parking page: {self.PARKING_URL}")

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
            filename = f"screenshots/error_parking_{safe_name}_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    # 🟢 הבדיקה המהירה (HREF Check)
    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        # 1. חיפוש האלמנט
        locator = (By.XPATH, self.GENERIC_LINK_XPATH.format(link_text))
        
        try:
            el = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            logger.error(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_text)
            return

        # 2. חילוץ URL ובדיקה מהירה
        href = el.get_attribute("href")
        orig_window = self.driver.current_window_handle

        try:
            # בדיקה מהירה ללא לחיצה
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed: {link_text}")
                    return 

            # 3. Fallback: לחיצה (אם ה-HREF לא תואם או חסר)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", el)

            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)

            current_url = unquote(self.driver.current_url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                logger.info(f"✅ Passed: {link_text}")
            else:
                logger.warning(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")

            self.driver.close()

        except Exception as e:
            logger.error(f"❌ Link error: '{link_text}' (Failed to open/verify). Error: {e}")
            self._take_error_screenshot(link_text)
        
        finally:
            try: self.driver.switch_to.window(orig_window)
            except: pass

    # --- פונקציות ניווט והרצה ---

    def run_tab_1_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Tab 1 - Fines) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_tab_3(self):
        logger.info("\n--- Navigating to Tab 3: תווי חניה ---")
        try:
            tab = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.TAB_3_LOCATOR))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", tab)
            logger.info(">>> Switched to Tab 3.")
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Failed to switch to Tab 3: {e}")
            self._take_error_screenshot("tab_switch_fail")

    def run_tab_3_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Tab 3 - Parking Permits) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)