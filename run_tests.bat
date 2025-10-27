@echo off
REM AI OS - Test Runner for Windows
echo 🧪 AI OS Test Suite - Windows Edition
echo =====================================

REM Activate environment
call ai-os-env\Scripts\activate.bat

echo.
echo 📦 Testing Dependencies...
echo -------------------------
python scripts/test_dependencies.py
if %errorlevel% neq 0 (
    echo ❌ Dependency tests failed!
    pause
    exit /b 1
)

echo.
echo 🧠 Testing AI Engine...
echo -----------------------
python tests/test_ai_engine.py
if %errorlevel% neq 0 (
    echo ❌ AI Engine tests failed!
    pause
    exit /b 1
)

echo.
echo 🐚 Testing Shell Interface...
echo -----------------------------
python tests/test_shell.py
if %errorlevel% neq 0 (
    echo ❌ Shell tests failed!
    pause
    exit /b 1
)

echo.
echo 🎉 All tests passed successfully!
echo =================================
echo.
echo Your AI OS is ready for Phase 2 development!
echo.
echo Next steps:
echo 1. Open VS Code: code .
echo 2. Start developing the dashboard UI
echo 3. Enhance AI capabilities
echo.
pause