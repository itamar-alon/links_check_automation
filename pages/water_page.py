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

class WaterPage(BasePage):
    """
    Water Interface Page Object.
    Optimized for SPEED + Clean Structure (like BusinessLicensePage).
    """

    # --- Locators & Constants ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"
    
    # 🟢 הגדרת שמות הטאבים כאן (קל לשינוי בעתיד)
    TAB_BUTTON_NAME_2 = "טפסים מקוונים"
    TAB_BUTTON_NAME_3 = "טפסים להורדה"

    # יצירת לוקייטורים דינמית לפי השמות
    TAB_2_LOCATOR = (By.XPATH, f"//button[contains(text(), '{TAB_BUTTON_NAME_2}')]")
    TAB_3_LOCATOR = (By.XPATH, f"//button[contains(text(), '{TAB_BUTTON_NAME_3}')]")

    # --- Data ---
    
    DEFAULT_TAB_LINKS = {
        "תשלום חשבון מים": "https://www.mast.co.il/15657/payment"
    }


    TAB_2_LINKS = {
        "נפשות": "nefashot",        
        "צריכת": "meshutefet",       
        "הפקדת מפתח": "form_6",  
        "ביוב": "form_3_pinui_biuv.aspx", 
        "בירור חיוב": "15657/form/b09e2646-cacf-4b5a-a149-4fca325255d2",   
        "בתעריף מיוחד": "form_5", 
        "הכרה בתעריף": "99c4dcdd",  
        "קריאת מונה": "b6baba35",   
        "איכות מים": "form_9"    
    }

    TAB_3_LINKS = {
        "בקשה לביקור": "setvisit.pdf",
        "בקשה לקבלת": "מידע.pdf",
        "הוראה": "מונגש",
        "החלפת": "החלפת",
        "סניטרית": "סניטרית",
        "הנדרשים": "טופס",
        "כשרות": "קרמ.pdf"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 3 
        self.WATER_URL = url

    def open_water_page(self):
        self.go_to_url(self.WATER_URL)

    def get_page_title(self):
        return self.driver.title

    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.now().strftime("%H%M%S") 
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            self.driver.save_screenshot(f"screenshots/err_{safe_name}_{timestamp}.png")
        except:
            pass

    # 🟢 הלוגיקה המהירה (HREF first, Click fallback)
    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}...") 
        
        locator = (By.XPATH, self.GENERIC_LINK_XPATH.format(link_text))
        
        try:
            el = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            logger.error(f"❌ Not Found: {link_text}")
            self._take_error_screenshot(link_text)
            return

        href = el.get_attribute("href")
        
        # ניקוי ה-URLים להשוואה קלה יותר
        clean_href = unquote(href).replace("https://", "").replace("http://", "") if href else ""
        clean_expected = unquote(expected_url_part).replace("https://", "").replace("http://", "")

        # 🚀 בדיקה מהירה
        if clean_expected in clean_href:
            logger.info(f"✅ OK (HREF): {link_text}")
            return 

        # Fallback: לחיצה
        logger.warning(f"⚠️ HREF mismatch for {link_text}, clicking...")
        
        orig_window = self.driver.current_window_handle
        try:
            self.driver.execute_script("arguments[0].target='_blank'; arguments[0].click();", el)
            
            WebDriverWait(self.driver, 5).until(EC.number_of_windows_to_be(2))
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)
            
            current_url = unquote(self.driver.current_url)
            self.driver.close()
            self.driver.switch_to.window(orig_window)

            clean_current = current_url.replace("https://", "").replace("http://", "")
            
            if clean_expected in clean_current:
                logger.info(f"✅ OK (Clicked): {link_text}")
            else:
                logger.error(f"❌ URL Mismatch for {link_text}")
                logger.error(f"   Exp: ...{clean_expected[-30:]}")
                logger.error(f"   Got: ...{clean_current[-30:]}")
                self._take_error_screenshot(link_text)

        except Exception as e:
            logger.error(f"❌ Click Failed for {link_text}: {e}")
            self.driver.switch_to.window(orig_window)

    # 🟢 פונקציות ניווט מעודכנות (עם הדפסה ברורה של שם הטאב)
    def navigate_to_tab_2(self):
        logger.info(f"\n--- Navigating to Tab 2: {self.TAB_BUTTON_NAME_2} ---")
        self._switch_tab(self.TAB_2_LOCATOR)

    def navigate_to_tab_3(self):
        logger.info(f"\n--- Navigating to Tab 3: {self.TAB_BUTTON_NAME_3} ---")
        self._switch_tab(self.TAB_3_LOCATOR)

    def _switch_tab(self, locator):
        try:
            time.sleep(0.5) 
            tab = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].click();", tab)
            logger.info(f">>> Switched successfully.")
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"❌ Failed to switch tab: {e}")
            raise e

    def run_tab_1_external_link_tests(self):
        for k, v in self.DEFAULT_TAB_LINKS.items(): self._verify_external_link(k, v)

    def run_tab_2_external_link_tests(self):
        for k, v in self.TAB_2_LINKS.items(): self._verify_external_link(k, v)

    def run_tab_3_external_link_tests(self):
        for k, v in self.TAB_3_LINKS.items(): self._verify_external_link(k, v)