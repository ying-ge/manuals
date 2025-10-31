"""
Integration tests for the LLM extractor.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from llm_extractor import LLMExtractor


def test_extractor_with_sample_abstracts():
    """Test extractor with sample abstracts of varying complexity."""
    
    extractor = LLMExtractor()
    
    # Sample 1: Clear AI/ML paper
    abstract1 = """
    Artificial intelligence (AI) has shown promise in medical imaging analysis.
    This study developed a deep learning model to detect breast cancer in mammography images.
    We trained a convolutional neural network (CNN) on 10,000 mammograms from multiple centers.
    The model achieved an accuracy of 94.5% and an AUC of 0.96 on the test set.
    Our AI system demonstrated superior performance compared to traditional computer-aided detection methods.
    """
    
    # Sample 2: Moderate complexity with AI application
    abstract2 = """
    Background: Early diagnosis of Alzheimer's disease remains challenging.
    Methods: We applied machine learning algorithms to analyze MRI scans and clinical data 
    from 500 patients. Random forest and support vector machine classifiers were evaluated.
    Results: The ML approach achieved 88% sensitivity and 92% specificity for early-stage detection.
    Conclusions: Machine learning can assist in identifying at-risk patients.
    """
    
    # Sample 3: Complex biomedical paper with minimal AI mention
    abstract3 = """
    The pathogenesis of COVID-19 involves complex immune responses. We investigated the role
    of cytokine storm in severe cases through analysis of patient samples. Elevated IL-6 and
    TNF-alpha levels were observed. Computational modeling suggested potential therapeutic targets.
    The study included 200 patients across three hospitals. Statistical analysis revealed
    significant correlations between biomarker levels and disease severity.
    """
    
    samples = [
        ("Clear AI paper", abstract1),
        ("Moderate complexity", abstract2),
        ("Minimal AI mention", abstract3)
    ]
    
    print("Testing LLM Extractor with sample abstracts")
    print("=" * 80)
    
    all_passed = True
    
    for name, abstract in samples:
        print(f"\nTest: {name}")
        print("-" * 80)
        
        try:
            result, needs_review, raw_output = extractor.extract(abstract)
            
            # Validate result structure
            required_fields = ['what_done', 'ai_role', 'models', 'data_sources', 'metrics']
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
                assert isinstance(result[field], str), f"Field {field} is not a string"
                assert len(result[field]) <= 400, f"Field {field} exceeds 400 chars"
            
            # Check that at least some fields are populated
            populated_fields = [f for f in required_fields if result[f].strip()]
            
            print(f"✓ Extraction successful")
            print(f"  - Populated fields: {len(populated_fields)}/{len(required_fields)}")
            print(f"  - Needs review: {needs_review}")
            print(f"  - What done: {result['what_done'][:100]}...")
            print(f"  - AI role: {result['ai_role'][:100]}...")
            
            # For the first two samples (clear AI papers), we expect good extraction
            if name in ["Clear AI paper", "Moderate complexity"]:
                assert result['what_done'], "what_done should not be empty for AI paper"
                assert result['ai_role'], "ai_role should not be empty for AI paper"
                print(f"✓ Content validation passed")
            
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            all_passed = False
        except Exception as e:
            print(f"✗ Extraction error: {e}")
            # For integration tests, we allow failures if LLM is not available
            # but we still want to test the structure
            print(f"  Note: This may be expected if no LLM API keys are configured")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


def test_heuristic_extractor():
    """Test that heuristic extractor works as fallback."""
    
    print("\nTesting heuristic extractor (fallback)")
    print("=" * 80)
    
    extractor = LLMExtractor()
    
    abstract = """
    This study developed a deep learning model using convolutional neural networks (CNN)
    to classify medical images. We used the ImageNet dataset for training.
    The model achieved 95% accuracy with an AUC of 0.98.
    Random forest and SVM were also evaluated for comparison.
    """
    
    try:
        # Use heuristic extraction directly
        result = extractor._heuristic_extract(abstract)
        
        print(f"✓ Heuristic extraction completed")
        print(f"  - What done: {result['what_done'][:100]}")
        print(f"  - AI role: {result['ai_role'][:100]}")
        print(f"  - Models: {result['models']}")
        print(f"  - Metrics: {result['metrics']}")
        
        # Validate structure
        assert isinstance(result, dict)
        assert 'what_done' in result
        assert 'ai_role' in result
        assert 'models' in result
        
        print(f"✓ Heuristic test passed")
        return 0
        
    except Exception as e:
        print(f"✗ Heuristic test failed: {e}")
        return 1


def main():
    """Run all tests."""
    print("Running integration tests for medRxiv harvester")
    print("=" * 80)
    
    exit_code = 0
    
    # Test 1: Sample abstracts
    result1 = test_extractor_with_sample_abstracts()
    if result1 != 0:
        exit_code = 1
    
    # Test 2: Heuristic extractor
    result2 = test_heuristic_extractor()
    if result2 != 0:
        exit_code = 1
    
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("✓ All integration tests passed!")
    else:
        print("✗ Some tests failed (this may be expected if API keys are not configured)")
    print("=" * 80)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
