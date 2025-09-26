#!/bin/bash

# eConsultation Sentiment Analysis Platform - Installation Script

echo "🚀 Installing eConsultation Sentiment Analysis Platform..."
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📋 Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "📥 Downloading NLTK data..."
python3 -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️ Warning: Could not download NLTK data: {e}')
"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run the app: streamlit run app.py"
echo "   3. Open browser: http://localhost:8501"
echo ""
echo "📚 For more information, see README.md"
echo "=================================================="
