@echo off
chcp 65001 >nul
echo ========================================
echo Python and Streamlit Environment Check
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is NOT installed or not in PATH
    echo.
    echo Installation steps:
    echo   1. Visit https://www.python.org/downloads/
    echo   2. Download Python 3.8 or higher
    echo   3. During installation, check "Add Python to PATH"
    echo   4. Run this script again after installation
    echo.
) else (
    python --version
    echo [OK] Python is installed
    for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
    echo    Python path: %PYTHON_PATH%
    echo.
)

REM Check pip
echo [2/4] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [X] pip is NOT installed
    echo.
) else (
    python -m pip --version
    echo [OK] pip is installed
    echo.
)

REM Check Streamlit
echo [3/4] Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [X] Streamlit is NOT installed
    echo.
    echo Installation command:
    echo   python -m pip install streamlit
    echo   OR
    echo   python -m pip install -r requirements.txt
    echo.
) else (
    for /f "tokens=*" %%i in ('python -c "import streamlit; print(streamlit.__version__)"') do set STREAMLIT_VER=%%i
    echo [OK] Streamlit is installed (version: %STREAMLIT_VER%)
    echo.
)

REM Check other dependencies
echo [4/4] Checking project dependencies...
python -c "import langchain" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] langchain is NOT installed
) else (
    echo [OK] langchain is installed
)

python -c "import langchain_openai" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] langchain-openai is NOT installed
) else (
    echo [OK] langchain-openai is installed
)

python -c "import openai" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] openai is NOT installed
) else (
    echo [OK] openai is installed
)

python -c "import dotenv" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] python-dotenv is NOT installed
) else (
    echo [OK] python-dotenv is installed
)

echo.
echo ========================================
echo Check completed
echo ========================================
echo.
echo Tip: If any packages are missing, run:
echo   python -m pip install -r requirements.txt
echo.
pause

