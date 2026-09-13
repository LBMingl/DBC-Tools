@echo off
echo ====================================
echo dbcCompare Build Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller dbcCompare.spec --clean
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo ====================================
echo Build completed successfully!
echo Executable location: dist\dbcCompare\dbcCompare.exe
echo ====================================
pause
