import pytest
import sys
import logging
import requests
import time
import os
import platform  
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 

class LokiHandler(logging.Handler):
    def __init__(self, url, job_name):
        super().__init__()
        self.url = url
        self.job_name = job_name

    def emit(self, record):
        try:
            ts = str(int(time.time() * 1e9))
            log_msg = self.format(record)
            payload = {
                "streams": [{
                    "stream": {"job": self.job_name, "level": record.levelname.lower()},
                    "values": [[ts, log_msg]]
                }]
            }
            requests.post(self.url, json=payload, timeout=2)
        except Exception:
            pass

log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_filename = log_dir / f"test_run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logger = logging.getLogger("SystemFlowLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    loki_handler = LokiHandler(url="http://10.77.72.45:3100/loki/api/v1/push", job_name="links_automation")
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)

logger.propagate = False

def is_running_on_server():
    """ 
    פונקציה שבודקת האם אנחנו על השרת. 
    """
    server_names = ["SERVER-PROD", "NODE-01"] 
    current_node = platform.node()
    return current_node in server_names or os.environ.get("RUN_ENV") == "server"

@pytest.fixture(scope="session", autouse=True)
def cleanup_zombies_before_run():
    """ מנקה שאריות תהליכים בצורה בטוחה לפני תחילת הריצה """
    if is_running_on_server():
        logger.info("🧹 Server detected: Cleaning up all Chrome and Driver processes...")
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
    else:
        logger.info("💻 Local PC detected: Cleaning only chromedriver to avoid closing personal tabs...")
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
    
    time.sleep(1)

@pytest.fixture(scope="session")
def secrets():
    data = load_secrets()
    if not data:
        logger.error("❌ Error: Could not load secrets.json")
        pytest.fail("❌ Error: Could not load secrets.json")
    return data

@pytest.fixture(scope="function")
def driver():
    logger.info("🌐 Initializing Chrome WebDriver...")
    
    chrome_options = Options()
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    chrome_options.add_argument("--window-size=1920,1080")

    if is_running_on_server():
        logger.info("🚀 Running in Headless mode (Server Optimization active)")
        chrome_options.add_argument("--headless=new")
    else:
        logger.info("🖥️ Running in Headed mode (Local PC)")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        if not is_running_on_server():
            driver.maximize_window()
            
        driver.broken_links_list = [] 
        
        yield driver
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize WebDriver: {e}")
        raise
        
    finally:
        logger.info("🛑 Closing Chrome WebDriver...")
        if 'driver' in locals():
            try:
                driver.quit()
            except Exception as quit_error:
                logger.warning(f"⚠️ Failed to close driver: {quit_error}")