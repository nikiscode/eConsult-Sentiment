@echo off
REM Windows startup script for eConsultation Sentiment Analysis Platform
REM This script handles Windows-specific signal and threading issues

echo 🚀 Starting eConsultation Sentiment Analysis Platform for Windows...
echo ================================================================

REM Set environment variables to prevent threading issues
set TOKENIZERS_PARALLELISM=false
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set NUMBA_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set VECLIB_MAXIMUM_THREADS=1
set NUMEXPR_MAX_THREADS=1
set CUDA_VISIBLE_DEVICES=
set PYTHONHASHSEED=0

REM Additional Windows-specific settings
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo 📊 Environment variables set for Windows compatibility
echo 🔧 Starting Streamlit application...

REM Start the application
python -m streamlit run app.py --server.port 8501 --server.headless true

echo.
echo 👋 Application stopped
pause
