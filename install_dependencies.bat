@echo off
chcp 65001 >nul
echo ========================================
echo Installing Project Dependencies
echo ========================================
echo.

REM Check Python first
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python first:
    echo   1. Visit https://www.python.org/downloads/
    echo   2. Download Python 3.8 or higher
    echo   3. During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Upgrade pip
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [2/3] Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed
    echo.
    echo Trying with Chinese mirror (if network issue)...
    python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [ERROR] Installation failed even with mirror
        pause
        exit /b 1
    )
)
echo.

REM Verify installation
echo [3/3] Verifying installation...
python -c "import streamlit; print('[OK] Streamlit:', streamlit.__version__)" 2>nul || echo [ERROR] Streamlit not installed
python -c "import langchain; print('[OK] LangChain installed')" 2>nul || echo [ERROR] LangChain not installed
python -c "import openai; print('[OK] OpenAI installed')" 2>nul || echo [ERROR] OpenAI not installed
echo.

echo ========================================
echo Installation completed!
echo ========================================
echo.
echo You can now run the application with:
echo   run.bat
echo   OR
echo   python -m streamlit run app.py
echo.
pause

