@echo off
REM AI OS - Environment Activation Helper for Windows
echo 🚀 Activating AI OS Development Environment...
echo =============================================

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "ai-os-env\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run phase1-setup-windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call ai-os-env\Scripts\activate.bat

echo ✅ AI OS environment activated!
echo.
echo 📋 Available commands:
echo   python scripts/test_dependencies.py    - Test all dependencies
echo   python tests/test_ai_engine.py         - Test AI engine
echo   python tests/test_shell.py             - Test shell interface
echo   python src/shell/ai_shell.py           - Start AI shell
echo.
echo 💡 VS Code: Open project with 'code .'
echo 🔧 Deactivate: Type 'deactivate' when done
echo.

REM Keep command prompt open
cmd /k