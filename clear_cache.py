#!/usr/bin/env python3
"""
Script to clear the extraction cache to force re-processing with updated configuration.
"""
import json
import os
from pathlib import Path

def clear_cache():
    """Clear the processed article cache."""
    cache_file = Path('.cache/processed.json')

    if cache_file.exists():
        print(f"🗑️ Removing cache file: {cache_file}")
        cache_file.unlink()
        print("✅ Cache cleared successfully")
    else:
        print("ℹ️ No cache file found")

def check_env_vars():
    """Check and display current environment variables."""
    print("🔍 Current GLM Configuration:")
    print(f"GLM_API_KEY: {'✅ Set' if os.getenv('GLM_API_KEY') else '❌ Missing'}")
    print(f"GLM_BASE_URL: {os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')}")
    print(f"GLM_MODEL_NAME: {os.getenv('GLM_MODEL_NAME', 'glm-4.6')}")

if __name__ == '__main__':
    print("🧹 Clearing GLM extraction cache...\n")

    check_env_vars()
    print()
    clear_cache()

    print("\n💡 Next steps:")
    print("1. Run 'python test_glm_api.py' to verify configuration")
    print("2. Run 'python src/harvest_medrxiv.py' to process articles")
    print("3. Check logs/ directory for detailed extraction logs")