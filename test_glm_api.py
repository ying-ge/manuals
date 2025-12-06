#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify GLM API configuration and extraction quality.
"""
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_glm_client():
    """Test GLM client initialization and API call."""
    print("[TEST] Testing GLM Client...")

    try:
        from glm_client import GLMClient

        # Check environment variables
        api_key_status = "SET" if os.getenv('GLM_API_KEY') else "MISSING"
        print(f"[INFO] GLM_API_KEY: {api_key_status}")
        print(f"[INFO] GLM_BASE_URL: {os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')}")
        print(f"[INFO] GLM_MODEL_NAME: {os.getenv('GLM_MODEL_NAME', 'glm-4.6')}")

        if not os.getenv('GLM_API_KEY'):
            print("[ERROR] GLM_API_KEY not found in environment variables")
            return False

        # Initialize client
        client = GLMClient()
        print("[SUCCESS] GLM client initialized successfully")

        # Test with a sample abstract
        test_abstract = """
        Background: Artificial intelligence (AI) has transformed medical diagnostics through deep learning algorithms
        that can detect patterns in medical imaging with high accuracy. This study evaluates the performance of
        a novel convolutional neural network (CNN) model for early detection of diabetic retinopathy from
        retinal fundus photographs.

        Methods: We developed and validated a deep learning model using a dataset of 100,000 retinal images
        from multiple institutions. The model was trained on 80% of the data and tested on the remaining 20%.
        We used area under the receiver operating characteristic curve (AUC), sensitivity, and specificity
        as primary performance metrics.

        Results: The CNN model achieved an AUC of 0.98 (95% CI: 0.97-0.99), sensitivity of 96.5%, and specificity
        of 94.2% for detecting referable diabetic retinopathy. The model outperformed human ophthalmologists
        in detecting early-stage disease while maintaining comparable performance for advanced cases.

        Conclusions: AI-based screening for diabetic retinopathy shows promise for improving early detection
        rates and reducing healthcare burden through automated, scalable screening solutions.
        """

        print("\n[TEST] Testing extraction with sample abstract...")
        result = client.extract_structured_info(test_abstract)

        print("\n[RESULT] Extraction Results:")
        what_done = result.get('what_done', 'N/A')
        ai_role = result.get('ai_role', 'N/A')
        models = result.get('models', 'N/A')
        data_sources = result.get('data_sources', 'N/A')
        metrics = result.get('metrics', 'N/A')

        print(f"What done (length: {len(what_done)}): {what_done[:200]}...")
        print(f"AI role (length: {len(ai_role)}): {ai_role[:200]}...")
        print(f"Models: {models}")
        print(f"Data sources: {data_sources}")
        print(f"Metrics: {metrics}")

        # Check quality
        what_done_len = len(result.get('what_done', ''))
        ai_role_len = len(result.get('ai_role', ''))
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in what_done + ai_role)

        print(f"\n[QUALITY] Quality Assessment:")
        print(f"What done length: {what_done_len} chars {'PASS' if what_done_len > 100 else 'FAIL'}")
        print(f"AI role length: {ai_role_len} chars {'PASS' if ai_role_len > 50 else 'FAIL'}")
        print(f"Chinese content: {'PASS' if is_chinese else 'FAIL'}")

        if what_done_len > 100 and ai_role_len > 50 and is_chinese:
            print("[SUCCESS] GLM API is working correctly with high-quality Chinese extraction!")
            return True
        else:
            print("[WARNING] GLM API returned results but quality may be suboptimal")
            return False

    except Exception as e:
        print(f"[ERROR] GLM client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_extractor():
    """Test the complete LLM extractor with fallback logic."""
    print("\n[TEST] Testing LLM Extractor...")

    try:
        from llm_extractor import LLMExtractor

        extractor = LLMExtractor()

        glm_status = "AVAILABLE" if extractor.glm_client else "UNAVAILABLE"
        openai_status = "AVAILABLE" if extractor.openai_client else "UNAVAILABLE"
        print(f"[INFO] GLM client: {glm_status}")
        print(f"[INFO] OpenAI client: {openai_status}")

        test_abstract = """
        This study developed a machine learning algorithm to predict patient outcomes in intensive care units
        using electronic health record data. The random forest model was trained on 50,000 patient records
        and achieved 85% accuracy in predicting mortality risk.
        """

        result, needs_review, raw_output = extractor.extract(test_abstract)

        print(f"\n[RESULT] Extractor Results:")
        print(f"Needs manual review: {'YES' if needs_review else 'NO'}")
        print(f"What done: {result.get('what_done', 'N/A')[:100]}...")
        print(f"AI role: {result.get('ai_role', 'N/A')[:100]}...")

        return True

    except Exception as e:
        print(f"[ERROR] LLM extractor test failed: {e}")
        return False

if __name__ == '__main__':
    print("[START] Starting GLM API Configuration Test\n")

    # Test GLM client
    glm_success = test_glm_client()

    # Test LLM extractor
    extractor_success = test_llm_extractor()

    print(f"\n[SUMMARY] Test Summary:")
    print(f"GLM Client: {'PASS' if glm_success else 'FAIL'}")
    print(f"LLM Extractor: {'PASS' if extractor_success else 'FAIL'}")

    if glm_success and extractor_success:
        print("\n[SUCCESS] All tests passed! GLM API is configured correctly.")
        sys.exit(0)
    else:
        print("\n[FAILED] Some tests failed. Check configuration.")
        sys.exit(1)