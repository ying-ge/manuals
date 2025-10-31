#!/usr/bin/env python3
"""
Local testing tool for running a single harvest.

Usage: 
  # Default (30 days, "artificial intelligence")
  python tools/run_once.py
  
  # Full 2025 harvest (all of 2025)
  DAYS_BACK=365 python tools/run_once.py
  
  # Custom keyword and time range
  SEARCH_KEYWORD="machine learning" DAYS_BACK=7 python tools/run_once.py
"""
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"Loaded environment from {dotenv_path}")
    else:
        print(f"No .env file found at {dotenv_path}")
        print("Make sure to set environment variables or create .env file")
except ImportError:
    print("python-dotenv not installed. Install it with: pip install python-dotenv")
    print("Or set environment variables manually")

# Import and run harvester
try:
    from harvest_medrxiv import main
    
    print("=" * 80)
    print("Starting medRxiv AI Article Harvest (Local Test)")
    print("=" * 80)
    print()
    
    # Check for required environment variables
    required_vars = ['GLM_API_KEY']
    optional_vars = ['OPENAI_API_KEY', 'BIO_MODEL_API_KEY', 'BIO_MODEL_BASE_URL']
    
    print("Environment Check:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✓ Set" if value else "✗ NOT SET (REQUIRED)"
        print(f"  {var}: {status}")
    
    for var in optional_vars:
        value = os.getenv(var)
        status = "✓ Set" if value else "○ Not set (optional)"
        print(f"  {var}: {status}")
    
    print()
    print("Configuration:")
    keyword = os.getenv('SEARCH_KEYWORD', 'artificial intelligence')
    days = os.getenv('DAYS_BACK', '30')
    print(f"  SEARCH_KEYWORD: {keyword}")
    print(f"  DAYS_BACK: {days}")
    print()
    
    # Check if required vars are set
    missing_required = [var for var in required_vars if not os.getenv(var)]
    if missing_required:
        print(f"ERROR: Required environment variables missing: {', '.join(missing_required)}")
        print("Please set them in .env file or as environment variables")
        sys.exit(1)
    
    # Run the harvest
    exit_code = main()
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✓ Harvest completed successfully!")
        print("Check the data/ directory for output files")
    else:
        print("✗ Harvest failed. Check logs/harvest.log for details")
    print("=" * 80)
    
    sys.exit(exit_code)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
