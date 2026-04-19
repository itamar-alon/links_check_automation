@echo off
set PROJECT_DIR=C:\Rizone\Projects\links
cd /d "%PROJECT_DIR%"

taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1

if not exist "allure-results" mkdir allure-results

echo 🚀 Starting System Integrity Scan...
echo Working Directory: %cd%

python -m pytest "%PROJECT_DIR%\tests\test_full_flow.py" --alluredir="%PROJECT_DIR%\allure-results"

set TEST_EXIT_CODE=%ERRORLEVEL%

echo Scan finished at %date% %time% with exit code %TEST_EXIT_CODE% >> run_history.log

if %TEST_EXIT_CODE% NEQ 0 (
    echo ❌ Scan failed with code %TEST_EXIT_CODE%.
) else (
    echo ✅ Scan completed successfully.
)

echo 👋 Closing session...
exit /b %TEST_EXIT_CODE%