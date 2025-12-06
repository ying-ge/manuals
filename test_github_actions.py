#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to run in GitHub Actions environment to verify GLM API configuration.
"""
import os
import sys
import json
from datetime import datetime

def print_github_action_summary():
    """Print summary for GitHub Actions."""
    print("::group::GLM API Configuration Test")

    # Check environment variables
    api_key = os.getenv('GLM_API_KEY')
    base_url = os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
    model_name = os.getenv('GLM_MODEL_NAME', 'glm-4.6')

    print(f"GLM_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"GLM_BASE_URL: {base_url}")
    print(f"GLM_MODEL_NAME: {model_name}")

    if api_key:
        # Mask the API key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"GLM_API_KEY (masked): {masked_key}")

    print("::endgroup::")

def test_glm_in_github_actions():
    """Test GLM client in GitHub Actions environment."""
    print("::group::GLM Client Test")

    try:
        # Add src to path
        sys.path.insert(0, 'src')
        from glm_client import GLMClient

        if not os.getenv('GLM_API_KEY'):
            print("❌ GLM_API_KEY not found in environment")
            return False

        client = GLMClient()
        print("✅ GLM client initialized successfully")

        # Test extraction
        test_abstract = """
        This study developed an artificial intelligence system for medical diagnosis using deep learning.
        The neural network was trained on 10,000 patient records and achieved 95% accuracy in disease detection.
        The AI system can process medical images and provide diagnostic recommendations to clinicians.
        """

        result = client.extract_structured_info(test_abstract)

        print("✅ GLM extraction completed")
        print(f"What done length: {len(result.get('what_done', ''))}")
        print(f"AI role length: {len(result.get('ai_role', ''))}")

        # Check for Chinese content
        what_done = result.get('what_done', '')
        ai_role = result.get('ai_role', '')
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in what_done + ai_role)
        print(f"Chinese content: {'✅ Yes' if has_chinese else '❌ No'}")

        return True

    except Exception as e:
        print(f"❌ GLM client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("::endgroup::")

def main():
    """Main test function."""
    print("🚀 GLM API Test for GitHub Actions")
    print(f"📅 Run at: {datetime.now().isoformat()}")

    print_github_action_summary()

    # Test GLM client
    glm_success = test_glm_in_github_actions()

    # Print final summary
    print("\n::group::Test Summary")
    print(f"GLM API Test: {'✅ PASS' if glm_success else '❌ FAIL'}")

    if glm_success:
        print("🎉 GitHub Actions is properly configured for GLM API!")
        print("✅ High-quality Chinese extraction should work correctly")
    else:
        print("⚠️ GitHub Actions GLM configuration needs attention")
        print("❌ Check repository secrets and API key validity")

    print("::endgroup::")

    # Exit with appropriate code
    sys.exit(0 if glm_success else 1)

if __name__ == '__main__':
    main()