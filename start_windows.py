#!/usr/bin/env python3
"""
Windows-specific startup script for eConsultation Sentiment Analysis Platform
This script handles Windows signal issues and starts the Streamlit application properly.
"""

import os
import sys
import platform
import warnings

def setup_windows_environment():
    """Setup environment specifically for Windows to prevent signal issues."""
    
    # Check if running on Windows
    if platform.system() != 'Windows':
        print("⚠️ This script is designed for Windows systems")
        return
    
    # Set environment variables to prevent threading issues
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["NUMBA_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_MAX_THREADS"] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    # Windows-specific settings
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    print("✅ Windows environment configured successfully")

def main():
    """Main function to start the application on Windows."""
    
    print("🪟 Windows Signal Fix for eConsultation Platform")
    print("=" * 50)
    
    # Setup Windows environment
    setup_windows_environment()
    
    try:
        # Import and run Streamlit
        import streamlit.web.cli as stcli
        
        print("🚀 Starting eConsultation Sentiment Analysis Platform...")
        print("📊 Application will be available at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Run the app with Windows-specific settings
        sys.argv = [
            "streamlit", 
            "run", 
            "app.py", 
            "--server.port", "8501", 
            "--server.headless", "true",
            "--server.address", "localhost"
        ]
        
        stcli.main()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Try running: python -m streamlit run app.py")
        print("3. Check if port 8501 is available")
        sys.exit(1)

if __name__ == "__main__":
    main()
