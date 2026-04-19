import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import logging

logger = logging.getLogger("SystemFlowLogger")

class BasePage:
    
    DEFAULT_WAIT_TIME = 10
    
    def __init__(self, driver=None):
        self.driver = driver
        if driver:
            self.wait = WebDriverWait(driver, self.DEFAULT_WAIT_TIME)

    def _get_wait(self, timeout):
        return WebDriverWait(self.driver, timeout if timeout is not None else self.DEFAULT_WAIT_TIME)

    def dismiss_cookie_banner(self):
        try:
            cookie_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'מאשר') or contains(text(), 'אישור') or contains(text(), 'הבנתי')]")
            cookie_btn.click()
            logger.info("🍪 Cookie banner closed successfully.")
        except NoSuchElementException:
            pass
        except Exception as e:
            logger.debug(f"⚠️ Cookie banner present but could not be clicked (ignoring).")

    def validate_link_status(self, url):
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
            if response.status_code >= 400:
                response = requests.get(url, allow_redirects=True, timeout=5, stream=True, headers=headers)
            
            is_success = response.status_code == 200
            
            if not is_success:
                self._record_broken_link(url, response.status_code)
                
            return is_success, response.status_code
            
        except Exception as e:
            self._record_broken_link(url, str(e))
            return False, str(e)

    def _record_broken_link(self, url, reason):
        if hasattr(self.driver, 'broken_links_list'):
            entry = f"URL: {url} | Reason/Status: {reason}"
            if entry not in self.driver.broken_links_list:
                self.driver.broken_links_list.append(entry)
                logger.warning(f"⚠️ Broken link recorded: {entry}")

    def go_to_url(self, url):
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
            logger.error(f"❌ Element not visible within timeout: {by_locator}")
            raise e

    def wait_for_clickable_element(self, by_locator, timeout=None):
        try:
            return self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator))
        except TimeoutException as e:
            logger.error(f"❌ Element not clickable within timeout: {by_locator}")
            raise e

    def wait_for_url_to_contain(self, url_part, timeout=None):
        try:
            self._get_wait(timeout).until(EC.url_contains(url_part))
        except TimeoutException as e:
            logger.error(f"❌ URL did not contain '{url_part}' within timeout.")
            raise e