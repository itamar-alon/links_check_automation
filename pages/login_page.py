from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from .base_page import BasePage
import time
import logging

logger = logging.getLogger("SystemFlowLogger")

class LoginPage(BasePage):
    """Class representing the Login page, supporting password login and login within a modal."""

    # --- Locators for main login page ---
    PASSWORD_TAB_TEXT = "באמצעות סיסמה"
    PASSWORD_TAB = (By.XPATH, f"//button[text()='{PASSWORD_TAB_TEXT}']")
    
    ID_FIELD = (By.XPATH, "//input[@name='identityNumber' or @name='tz' or @type='text' or @type='number']") 
    PASSWORD_FIELD = (By.NAME, "password") 
    
    FINAL_LOGIN_BUTTON_TEXT = "כניסה"
    FINAL_LOGIN_BUTTON = (By.XPATH, f"//button[text()='{FINAL_LOGIN_BUTTON_TEXT}']")
    
    OVERLAY_LOCATOR = (By.CSS_SELECTOR, ".MuiDialog-container[role='presentation']")

    def __init__(self, driver, url):
        super().__init__(driver) 
        self.LOGIN_URL = url 

    def login_with_password(self, user_id: str, user_password: str):
        """Performs a complete login using ID number and password on main login page."""
        
        self.go_to_url(self.LOGIN_URL)
        logger.info(f">>> Navigated to: {self.LOGIN_URL}")
        
        try:
            tab_element = self.wait_for_clickable_element(self.PASSWORD_TAB, timeout=10)
            self.execute_script("arguments[0].click();", tab_element)
            logger.info(f">>> Clicked on tab '{self.PASSWORD_TAB_TEXT}' (Safe Click).")
        except Exception:
            self.click(self.PASSWORD_TAB)
            logger.info(f">>> Clicked on tab '{self.PASSWORD_TAB_TEXT}' (Standard Click).")

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ID_FIELD)
        )
        
        self.enter_text(self.ID_FIELD, user_id) 
        logger.info(">>> Entered ID number")

        self.enter_text(self.PASSWORD_FIELD, user_password)
        logger.info(">>> Entered password")

        try:
            self.wait_for_invisibility(self.OVERLAY_LOCATOR, timeout=10)
        except TimeoutException:
            logger.warning(">>> Warning: Overlay did not disappear, attempting force click (JS).")

        login_button_element = self.wait_for_clickable_element(self.FINAL_LOGIN_BUTTON, timeout=5)
        self.execute_script("arguments[0].click();", login_button_element)
            
        logger.info(f">>> Clicked on button '{self.FINAL_LOGIN_BUTTON_TEXT}'.")

    def wait_for_successful_login(self, home_url_part: str):
        self.wait_for_url_to_contain(home_url_part, timeout=20)
        logger.info(f">>> Successful navigation to URL containing '{home_url_part}'.")

    def login_with_password_inside_modal(self, id_number: str, password: str):
        """Login inside modal with password tab selection first."""

        user_id_str = str(id_number)
        user_password_str = str(password)

        # 1. לחיצה על טאב 'באמצעות סיסמה' במודאל
        try:
            password_tab = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='באמצעות סיסמה']"))
            )
            password_tab.click()
            logger.info(">>> Clicked 'באמצעות סיסמה' tab inside modal")
            time.sleep(1.5)  # המתנה לטעינה
        except TimeoutException:
            logger.info(">>> 'באמצעות סיסמה' tab not found or already active, continuing...")

        # 2. הזנת תעודת זהות
        id_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='tz']"))
        )
        id_input.clear()
        id_input.send_keys(user_id_str)
        logger.info(">>> ID filled")

        # 3. הזנת סיסמה
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='password']"))
        )
        password_input.clear()
        password_input.send_keys(user_password_str)
        logger.info(">>> Password filled")

        # 4. לחיצה על כפתור כניסה בתוך המודאל
        modal_login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class, 'MuiDialog-container') and contains(@role, 'presentation')]//button[text()='כניסה' and @type='button']"
            ))
        )
        try:
            modal_login_button.click()
            logger.info(">>> Clicked login button normally")
        except ElementClickInterceptedException:
            logger.warning(">>> Click intercepted, retrying via JS")
            self.execute_script("arguments[0].click();", modal_login_button)

        # 5. המתנה שהמודאל יסגר (כדי לוודא הצלחה)
        try:
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-container') and contains(@role, 'presentation')]"))
            )
            logger.info(">>> Modal closed successfully")
        except TimeoutException:
            logger.warning(">>> Modal did NOT close – continue anyway")
