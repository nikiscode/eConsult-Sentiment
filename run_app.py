#!/usr/bin/env python3
"""
Startup script for eConsultation Sentiment Analysis Platform
This script handles signal issues and starts the Streamlit application properly.
"""

import os
import sys
import signal
import threading
import warnings
import subprocess

def setup_environment():
    """Setup environment to prevent signal and threading issues."""
    
    # Set environment variables to prevent threading issues
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["NUMBA_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_MAX_THREADS"] = "1"
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Set Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def signal_handler(signum, frame):
    """Handle signals gracefully."""
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to start the application."""
    
    # Setup environment
    setup_environment()
    
    # Set signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Import and run Streamlit
    try:
        import streamlit.web.cli as stcli
        
        # Start the app
        print("🚀 Starting eConsultation Sentiment Analysis Platform...")
        print("📊 Application will be available at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application")
        
        # Run the app
        sys.argv = ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
        stcli.main()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
