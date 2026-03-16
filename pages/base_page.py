import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger("SystemFlowLogger")

class BasePage:
    """ מחלקת בסיס המכילה פעולות נפוצות ואימות HTTP. """
    
    DEFAULT_WAIT_TIME = 10
    
    def __init__(self, driver=None):
        self.driver = driver
        if driver:
            self.wait = WebDriverWait(driver, self.DEFAULT_WAIT_TIME)

    def _get_wait(self, timeout):
        return WebDriverWait(self.driver, timeout if timeout is not None else self.DEFAULT_WAIT_TIME)

    def validate_link_status(self, url):
        """ בודק שהקישור מחזיר סטטוס 200 ללא טעינת הדף בדפדפן ומעדכן רשימת לינקים שבורים. """
        try:
            # שימוש ב-HEAD למהירות מירבית
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code >= 400: # אם HEAD נכשל, ננסה GET
                response = requests.get(url, allow_redirects=True, timeout=5, stream=True)
            
            is_success = response.status_code == 200
            
            # עדכון רשימת הלינקים השבורים בדרייבר אם הסטטוס אינו 200
            if not is_success:
                self._record_broken_link(url, response.status_code)
                
            return is_success, response.status_code
            
        except Exception as e:
            # במקרה של שגיאת התחברות (Timeout, DNS וכו')
            self._record_broken_link(url, str(e))
            return False, str(e)

    def _record_broken_link(self, url, reason):
        """ פונקציית עזר פנימית לרישום הלינק השבור בדרייבר """
        if hasattr(self.driver, 'broken_links_list'):
            entry = f"URL: {url} | Reason/Status: {reason}"
            if entry not in self.driver.broken_links_list:
                self.driver.broken_links_list.append(entry)
                # הוספת לוג: ברגע שמתגלה לינק שבור בזמן אמת, זה נכתב לקובץ!
                logger.warning(f"⚠️ Broken link recorded: {entry}")

    def go_to_url(self, url):
        # תיעוד מעבר בין עמודים
        logger.info(f"Navigating to URL: {url}")
        self.driver.get(url)

    def execute_script(self, script, element=None):
        if element:
            return self.driver.execute_script(script, element)
        return self.driver.execute_script(script)

    def get_element(self, by_locator, timeout=None):
        try:
            return self._get_wait(timeout).until(EC.visibility_of_element_located(by_locator))
        except TimeoutException as e:
            # תיעוד שגיאה למקרה שאלמנט לא הופיע
            logger.error(f"❌ Element not visible within timeout: {by_locator}")
            raise e

    def wait_for_clickable_element(self, by_locator, timeout=None):
        try:
            return self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator))
        except TimeoutException as e:
            # תיעוד שגיאה למקרה שאלמנט לא ניתן ללחיצה
            logger.error(f"❌ Element not clickable within timeout: {by_locator}")
            raise e

    def wait_for_url_to_contain(self, url_part, timeout=None):
        try:
            self._get_wait(timeout).until(EC.url_contains(url_part))
        except TimeoutException as e:
            # תיעוד שגיאה למקרה שה-URL לא השתנה כמצופה
            logger.error(f"❌ URL did not contain '{url_part}' within timeout.")
            raise e