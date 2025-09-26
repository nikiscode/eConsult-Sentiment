@echo off
REM eConsultation Sentiment Analysis Platform - Windows Installation Script

echo 🚀 Installing eConsultation Sentiment Analysis Platform...
echo ==================================================

REM Check Python version
python --version
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Download NLTK data
echo 📥 Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('vader_lexicon', quiet=True); print('✅ NLTK data downloaded successfully')"

echo.
echo ✅ Installation completed successfully!
echo.
echo 🚀 To start the application (Windows Signal Fix):
echo    1. Activate virtual environment: venv\Scripts\activate
echo    2. Run the app: start_windows.bat (recommended)
echo    3. Or run: python start_windows.py
echo    4. Or run: streamlit run app_windows.py
echo    5. Or run: streamlit run app.py (may have signal issues)
echo    6. Open browser: http://localhost:8501
echo.
echo 🔧 Windows Signal Fix:
echo    - Use start_windows.bat for best compatibility
echo    - Use app_windows.py for Windows-optimized version
echo    - Environment variables are set automatically
echo.
echo 📚 For more information, see README.md
echo ==================================================
pause
