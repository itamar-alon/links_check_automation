import pytest
import sys
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver

# --- Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 

# --- Custom Loki Handler ---
class LokiHandler(logging.Handler):
    """ Handler that pushes log records directly to a Grafana Loki API """
    def __init__(self, url, job_name):
        super().__init__()
        self.url = url
        self.job_name = job_name

    def emit(self, record):
        try:
            # Loki דורש חותמת זמן בננו-שניות
            ts = str(int(time.time() * 1e9))
            log_msg = self.format(record)
            
            payload = {
                "streams": [{
                    "stream": {
                        "job": self.job_name,
                        "level": record.levelname.lower()
                    },
                    "values": [[ts, log_msg]]
                }]
            }
            # Timeout קצר כדי שאם השרת למטה, זה לא יעכב את ריצת הטסט
            requests.post(self.url, json=payload, timeout=2)
        except Exception:
            # התעלמות משגיאות שליחה כדי לא לרסק את הטסט
            pass

# --- Logging Setup ---
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_filename = log_dir / f"test_run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logger = logging.getLogger("SystemFlowLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # 1. Handler לקובץ המקומי
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Handler לקונסולה
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 3. Handler ל-Loki!
    loki_handler = LokiHandler(url="http://10.77.72.45:3100/loki/api/v1/push", job_name="links_automation")
    loki_handler.setLevel(logging.INFO)
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)

logger.propagate = False

# --- Fixtures Global ---
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
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.broken_links_list = [] 
    yield driver
    logger.info("🛑 Closing Chrome WebDriver...")
    driver.quit()