# 🏙️ Municipal Services Automation

[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Framework-Selenium-green.svg)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/Runner-Pytest-yellow.svg)](https://docs.pytest.org/)
[![Allure](https://img.shields.io/badge/Reporting-Allure-orange.svg)](https://docs.qameta.io/allure/)

An advanced **End-to-End (E2E)** test automation framework designed to validate critical digital services for the Rishon LeZion Municipality. The framework simulates real user journeys across multiple modules (Water, Education, Parking, Business Licensing, etc.) to ensure system stability and link integrity.

---

## 🚀 Key Features

- **Page Object Model (POM)**: Built with a scalable architecture that strictly separates test logic (`tests/`) from page interaction logic (`pages/`), ensuring high maintainability.
- **Performance Optimization (Smart Verify)**: Implemented a "Smart Link Verification" mechanism. Instead of the slow "Click & Wait" approach, the framework performs static DOM analysis (href validation).
  - **Result**: Reduced "Water Interface" test execution time by **~80%** (from 6 minutes to ~1 minute).
- **Robust Error Handling**: Automatic screenshot capture upon test failure, saving artifacts with timestamps for rapid debugging.
- **Advanced Reporting**: Full integration with Allure Framework to generate detailed, interactive HTML reports with step-by-step execution logs.
- **Secure Configuration**: Sensitive data (credentials, URLs) is managed via an external `.env` file, keeping the codebase secure and Git-clean.

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Web Driver**: Selenium WebDriver
- **Test Runner**: Pytest
- **Reporting**: Allure Report
- **Configuration Management**: `python-dotenv`

---

## 📂 Project Structure

```text
├── pages/                  # Page Object Classes
│   ├── base_page.py        # Base class with Selenium wrappers & error handling
│   ├── water_page.py       # Water services logic (Optimized)
│   ├── education_page.py   # Education module logic
│   └── ...
├── tests/                  # Test Scripts (Pytest)
│   ├── test_full_flow.py   # Main E2E execution file
│   └── conftest.py         # Pytest fixtures and environment setup
├── screenshots/            # Error artifacts (Auto-generated)
├── .env                    # Sensitive credentials (Git Ignored)
├── .env_example            # Template for environment variables
├── requirements.txt        # Python dependencies
└── README.md
⚙️ Installation & Setup
1. Clone the Repository
Bash
git clone [https://github.com/itamar-alon/links_check_automation.git](https://github.com/itamar-alon/links_check_automation.git)
cd links_check_automation
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configuration (.env)
Create a .env file in the root directory. This file is ignored by Git. You can use .env_example as a template:

קטע קוד
# URLs
WATER_URL=https://...
EDUCATION_URL=https://...
BUSINESS_URL=https://...
DAYCARE_URL=https://...
PARKING_URL=https://...
ENFORCEMENT_URL=https://...
STREET_URL=https://...

# Credentials
ID_NUMBER=your_id_here
PASSWORD=your_password_here
🏃‍♂️ How to Run
Execute the Full System Test
Run the comprehensive suite using Pytest:

Bash
python -m pytest tests/test_full_flow.py --alluredir=./allure-results
View the Report
Generate and serve the Allure HTML report:

Bash
allure serve ./allure-results
📄 License
Internal project for Rishon LeZion Municipality.
