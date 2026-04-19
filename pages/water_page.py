from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from urllib.parse import unquote
import requests 
from .base_page import BasePage
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("SystemFlowLogger")

class WaterPage(BasePage):
    """
    Water Interface Page Object.
    Optimized for SPEED + Clean Structure (like BusinessLicensePage).
    """

    PAGE_TITLE = (By.TAG_NAME, "h1")
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"
    
    TAB_BUTTON_NAME_2 = "טפסים מקוונים"
    TAB_BUTTON_NAME_3 = "טפסים להורדה"


    TAB_2_LOCATOR = (By.XPATH, f"//button[contains(text(), '{TAB_BUTTON_NAME_2}')]")
    TAB_3_LOCATOR = (By.XPATH, f"//button[contains(text(), '{TAB_BUTTON_NAME_3}')]")

    
    DEFAULT_TAB_LINKS = {
        "תשלום חשבון מים": "https://www.mast.co.il/15657/payment"
    }

    TAB_2_LINKS = {
        "נפשות": "form_nefashot.aspx",        
        "צריכת": "meshutefet",       
        "הפקדת מפתח": "form_6",  
        "ביוב": "form_3_pinui_biuv.aspx", 
        "בירור חיוב": "form_8_zriha_meshutefet.aspx", 
        "בתעריף מיוחד": "form_5", 
        "הכרה בתעריף": "form_5_mad_meshuyah.aspx", 
        "קריאת מונה": "form_6_key.aspx", 
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

 
        href = el.get_attribute("href") or ""
        onclick = el.get_attribute("onclick") or ""
        combined_attributes = unquote(href + " " + onclick)
        clean_expected = unquote(expected_url_part).replace("https://", "").replace("http://", "").strip()


        if clean_expected not in combined_attributes.replace("https://", "").replace("http://", ""):
            logger.error(f"❌ Link Mismatch on Page for {link_text}")
            logger.error(f"   Expected to find: {clean_expected}")
            logger.error(f"   Attributes contained: {combined_attributes}")
            self._take_error_screenshot(link_name=link_text)
            return


        if href.startswith("http"):
            try:

                response = requests.get(href, timeout=10, allow_redirects=True, verify=False)
                
                if response.status_code == 404:
                    logger.error(f"❌ BROKEN LINK (404) for {link_text}: {href}")
                    self._take_error_screenshot(link_text)
                elif response.status_code >= 400:
                    logger.error(f"❌ SERVER ERROR ({response.status_code}) for {link_text}")
                else:
                    logger.info(f"✅ OK (Link is Alive - {response.status_code}): {link_text}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not verify link status for {link_text}: {e}")
        else:
            logger.info(f"✅ OK (Attribute Match, local link skipped HTTP check): {link_text}")

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