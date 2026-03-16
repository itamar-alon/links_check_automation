@echo off
:: הגדרת נתיב הפרויקט
set PROJECT_DIR=C:\Rizone\Projects\links
cd /d "%PROJECT_DIR%"

:: ניקוי תהליכי דפדפן ודרייברים תקועים מהרצות קודמות (מונע זומבים)
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1

:: יצירת תיקיית תוצאות אם חסרה
if not exist "allure-results" mkdir allure-results

echo 🚀 Starting System Integrity Scan...
echo Working Directory: %cd%

:: הרצה דרך מודול pytest
python -m pytest "%PROJECT_DIR%\tests\test_full_flow.py" --alluredir="%PROJECT_DIR%\allure-results"

:: שמירת ה-Exit Code של הטסט
set TEST_EXIT_CODE=%ERRORLEVEL%

:: תיעוד סיום
echo Scan finished at %date% %time% with exit code %TEST_EXIT_CODE% >> run_history.log

if %TEST_EXIT_CODE% NEQ 0 (
    echo ❌ Scan failed with code %TEST_EXIT_CODE%.
) else (
    echo ✅ Scan completed successfully.
)

:: סגירה אוטומטית ללא המתנה
echo 👋 Closing session...
exit /b %TEST_EXIT_CODE%