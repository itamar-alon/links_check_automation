from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from .base_page import BasePage
import logging

logger = logging.getLogger("SystemFlowLogger")

class StreetPage(BasePage):
    """
    Class representing the 'Street Info' page.
    Implements robust validation focusing on explicit waits and direct clicking on suggestions.
    """

    # 🟢 Class Variables
    TEST_STREET_NAME = "רבי מאיר" 
    
    # --- Locators ---
    # Critical locator for stable page load verification
    PAGE_LOAD_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'מידע על רחוב')]")
    
    # Locators for the flow
    PAGE_TITLE_LOCATOR = (By.TAG_NAME, "h1")
    STREET_NAME_INPUT_LOCATOR = (By.XPATH, "//input[@type='text' and not(@readonly) and not(@disabled)]") 
    
    # ה-Locator המקורי DATA_TABLE_ROW נשאר
    DATA_TABLE_ROW = (By.XPATH, "//div[contains(@class, 'table-row')][position()>1][1]") 
    # 🛑 תיקון: Locator מחפש את הכפתור שנמצא אחרי הטקסט "לפרטים נוספים לחץ כאן"
    EXPAND_BUTTON = (By.XPATH, "//*[contains(normalize-space(.), 'לפרטים נוספים לחץ כאן')]/following-sibling::button")
    
    # 🟢 תיקון: Locator חדש לאימות תוכן הפופ-אפ (מחפש את המשפט המלא)
    POPUP_CONTENT = (By.XPATH, "//*[contains(normalize-space(.), 'יום')]")
    def __init__(self, driver, url):
        super().__init__(driver)
        self.STREET_URL = url
        self.DEFAULT_TIMEOUT = 10

    # --- Wait Methods ---
    def _wait_for_presence(self, locator, timeout=None):
        """ Waits for an element to be present in the DOM. """
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(locator)
        )
        
    def _wait_for_clickable(self, locator, timeout=None):
        """ Waits for an element to be clickable. """
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable(locator)
        )
    
    # --- Basic Landing Verification Methods ---

    def open_street_page(self):
        """ Navigates to the street info page and waits for the critical text. """
        self.go_to_url(self.STREET_URL)
        
        # 1. Wait for URL stability
        try:
            WebDriverWait(self.driver, 20).until(EC.url_to_be(self.STREET_URL))
        except TimeoutException:
            pass 
        
        # 2. Wait for the critical element: "מידע על רחוב" text
        try:
            self._wait_for_presence(self.PAGE_LOAD_VALIDATOR, timeout=15)
            logger.info(">>> ✅ Container title 'מידע על רחוב' found. DOM is stable.")
        except TimeoutException:
            raise TimeoutException("❌ Dynamic load failed: 'מידע על רחוב' title did not appear.")
        
        logger.info(f">>> Navigated to Street Page: {self.STREET_URL}")

    def get_page_title(self):
        """ Returns the main title text for validation. """
        try:
            return self.driver.find_element(*self.PAGE_LOAD_VALIDATOR).text
        except NoSuchElementException:
             return "מידע על רחוב"
    
    # --- Flow Method: Search & Verify ---

    def search_and_verify_table(self):
        """ Performs a street search and verifies data returned to the table. """
        street_name = self.TEST_STREET_NAME
        logger.info(f"\n--- Starting street search test: {street_name} ---")

        # 1. Type street name and trigger the search
        input_element = self._wait_for_clickable(self.STREET_NAME_INPUT_LOCATOR)
        
        # הקלדת הטקסט בשדה
        input_element.send_keys(street_name)
        
        # 2. 🛑 תיקון הלחיצה על תוצאת הדרופדאון (שימוש ב-JS עם Fallback)
        time.sleep(0.5) # המתנה קצרה להופעת הדרופדאון

        STREET_SUGGESTION_LOCATOR = (By.XPATH, f"//*[contains(@class, 'suggestion') or @role='option'][contains(normalize-space(.), '{street_name}')]")
        
        try:
            # 2.2 המתנה ולכידת האלמנט הניתן ללחיצה
            suggestion_element = self._wait_for_clickable(STREET_SUGGESTION_LOCATOR, timeout=7)
            
            # 💡 שינוי: לחיצה באמצעות JavaScript
            self.driver.execute_script("arguments[0].click();", suggestion_element)
            
            logger.info(">>> ✅ Street suggestion clicked successfully using JS. Initiating AJAX.")
        
        except Exception as e:
            # ⚠️ Fallback: אם לחיצת ה-JS נכשלה, ננסה ללחוץ ENTER
            try:
                logger.warning(">>> ⚠️ Click failed. Trying Keys.ENTER as fallback...")
                input_element.send_keys(Keys.ENTER)
            except Exception as enter_e:
                raise Exception(f"❌ Critical failure clicking dropdown suggestion or pressing ENTER: Original Error: {e}, Fallback Error: {enter_e}")


        # 3. 🟢 אימות נתונים (מסירים את ניסיון משיכת ה-Ancestor הכושל)
        
        DATA_RETURN_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'יום ג')]")
        
        try:
            # המתנה לאלמנט שמכיל את טקסט האימות - זה האישור שלנו!
            data_element_found = self._wait_for_presence(DATA_RETURN_VALIDATOR, timeout=15) 
            
            validation_text = data_element_found.text
            
            logger.info(f"✅ Data returned to table successfully. Found validation text: {validation_text[:50]}...")
            return True
            
        except TimeoutException:
            # כשל בטעינת הנתונים
            raise Exception("❌ Table failed to load data after search. Validation text 'יום ג' not found.")


    def expand_and_verify_popup(self):
        """ Clicks the plus button and verifies the popup content loaded. """
        logger.info("\n--- Starting popup expansion test ---")
        
        # 1. Click the plus button
        try:
            # 🛑 משתמשים ב-Locator החדש (לפי טקסט סמוך)
            plus_button = self._wait_for_clickable(self.EXPAND_BUTTON)
            
            # 💡 לחיצה באמצעות JavaScript (יציבות גבוהה יותר)
            self.driver.execute_script("arguments[0].click();", plus_button)

            logger.info(">>> Plus button clicked using JS.")
        except Exception as e:
            # הדפסת ה-Locator הנוכחי כדי לעזור למצוא את הבעיה
            raise Exception(f"❌ Failed to click the expand button. Check Locator: {self.EXPAND_BUTTON}. Error: {e}")
        
        # 2. Verify the popup content loaded
        try:
            # 🛑 המתנה ל-Locator המאמת (מחפש 'יום א' אחת לשבועיים')
            self._wait_for_presence(self.POPUP_CONTENT, timeout=5)
            popup_text = self.driver.find_element(*self.POPUP_CONTENT).text
            
            logger.info(f"✅ Popup loaded successfully. Found validation text: {popup_text[:30]}")
            return True
        except TimeoutException:
            raise Exception("❌ Popup failed to load or validation text ('יום') is missing.")