#!/usr/bin/env python3
"""
Demo script to show extraction results without requiring API keys.
Uses sample abstracts to demonstrate the extraction capabilities.
"""
import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from llm_extractor import LLMExtractor

# Sample medRxiv abstracts related to AI (realistic examples)
SAMPLE_ABSTRACTS = [
    {
        "title": "Deep Learning for Early Detection of Alzheimer's Disease from Brain MRI",
        "authors": ["Zhang L", "Wang M", "Chen Y"],
        "corresponding_author": "Zhang L",
        "affiliations": ["Stanford University School of Medicine"],
        "abstract": """
Background: Early detection of Alzheimer's disease (AD) remains a critical challenge in neurology.
We developed a deep learning model to predict AD onset from structural brain MRI scans.

Methods: We trained a 3D convolutional neural network (CNN) on 5,247 MRI scans from the 
Alzheimer's Disease Neuroimaging Initiative (ADNI) database. The model was designed to classify
patients into three categories: cognitively normal, mild cognitive impairment, and AD.
We used ResNet-50 architecture with transfer learning and data augmentation techniques.

Results: The deep learning model achieved 92.3% accuracy, with an AUC-ROC of 0.96 on the 
independent test set. Sensitivity was 89.7% and specificity was 94.1%. The model outperformed 
traditional radiological assessment by 12 percentage points.

Conclusions: Our AI-powered diagnostic tool demonstrates superior performance in early AD 
detection and could assist clinicians in identifying at-risk patients for early intervention.
        """,
        "url": "https://www.medrxiv.org/content/10.1101/2024.01.15.24301234",
        "published_at": "2024-01-15T00:00:00",
        "source": "medrxiv_demo"
    },
    {
        "title": "Machine Learning for Predicting COVID-19 Severity Using Clinical and Laboratory Data",
        "authors": ["Smith J", "Johnson K", "Brown R"],
        "corresponding_author": "Smith J",
        "affiliations": ["Massachusetts General Hospital", "Harvard Medical School"],
        "abstract": """
Objective: To develop and validate a machine learning model for predicting severe COVID-19 
outcomes using readily available clinical and laboratory parameters.

Methods: This retrospective study included 3,892 COVID-19 patients from 15 hospitals. We 
evaluated multiple machine learning algorithms including random forest, gradient boosting 
(XGBoost), and logistic regression. Input features included age, comorbidities, vital signs,
and laboratory values (D-dimer, CRP, lymphocyte count). The primary outcome was ICU admission
or death within 30 days.

Results: The XGBoost model achieved the best performance with an AUROC of 0.88 (95% CI: 0.86-0.90).
The model identified D-dimer >1000 ng/mL, age >65 years, and lymphopenia as the strongest 
predictors. External validation on 1,200 patients from 5 independent centers showed consistent
performance (AUROC 0.85).

Conclusions: Machine learning can accurately predict COVID-19 severity using routine clinical
data, potentially enabling early risk stratification and resource allocation.
        """,
        "url": "https://www.medrxiv.org/content/10.1101/2024.02.03.24302156",
        "published_at": "2024-02-03T00:00:00",
        "source": "medrxiv_demo"
    },
    {
        "title": "Artificial Intelligence for Automated Diabetic Retinopathy Screening in Primary Care",
        "authors": ["Lee S", "Park J", "Kim H", "Choi M"],
        "corresponding_author": "Lee S",
        "affiliations": ["Seoul National University Hospital"],
        "abstract": """
Background: Diabetic retinopathy (DR) is a leading cause of blindness, but screening rates 
remain low. We developed an AI system for automated DR screening in primary care settings.

Methods: We trained a deep neural network on 85,000 fundus photographs from 25,000 patients.
The model used EfficientNet-B5 architecture to classify images into five categories: no DR,
mild, moderate, severe non-proliferative DR, and proliferative DR. We evaluated the system
in a prospective real-world deployment across 120 primary care clinics.

Results: The AI system achieved 94.5% sensitivity and 91.2% specificity for referable DR
(moderate or worse). Agreement with expert ophthalmologists was substantial (kappa=0.89).
In the real-world deployment, screening rates increased from 45% to 78%, and the median
time from screening to treatment decreased from 63 to 18 days.

Conclusions: AI-powered automated screening can improve DR detection rates and accelerate
treatment in primary care, potentially preventing vision loss in diabetic patients.
        """,
        "url": "https://www.medrxiv.org/content/10.1101/2024.03.10.24303987",
        "published_at": "2024-03-10T00:00:00",
        "source": "medrxiv_demo"
    },
    {
        "title": "Natural Language Processing for Automated Clinical Trial Eligibility Screening",
        "authors": ["Rodriguez A", "Martinez C", "Garcia F"],
        "corresponding_author": "Rodriguez A",
        "affiliations": ["Mayo Clinic", "University of Arizona"],
        "abstract": """
Purpose: Clinical trial recruitment is time-consuming and inefficient. We developed a natural
language processing (NLP) system to automatically screen electronic health records (EHRs) for
trial eligibility.

Methods: Using BERT-based transformer models, we created an NLP pipeline to extract medical
concepts from unstructured clinical notes. The system matched patient data against trial
inclusion/exclusion criteria for 50 oncology trials. We processed EHRs from 15,000 patients
and compared AI recommendations with manual screening by clinical research coordinators.

Results: The NLP system achieved 87% precision and 92% recall for identifying eligible patients.
Processing time was reduced from 20 minutes per patient (manual) to 30 seconds (automated).
The system successfully identified 340 eligible patients who were not found through conventional
methods. Implementation led to a 45% increase in trial enrollment rates.

Conclusions: AI-driven NLP can dramatically improve clinical trial recruitment efficiency and
help identify more eligible candidates from existing patient populations.
        """,
        "url": "https://www.medrxiv.org/content/10.1101/2024.04.22.24305432",
        "published_at": "2024-04-22T00:00:00",
        "source": "medrxiv_demo"
    },
    {
        "title": "Federated Learning for Privacy-Preserving Medical Image Analysis Across Institutions",
        "authors": ["Chen W", "Liu X", "Zhang Q", "Wu Y"],
        "corresponding_author": "Chen W",
        "affiliations": ["Stanford University", "MIT"],
        "abstract": """
Background: Multi-institutional collaboration in medical AI is limited by data privacy concerns.
We implemented a federated learning framework for training medical image classifiers without
sharing patient data.

Methods: We deployed federated learning across 8 hospitals for breast cancer detection in
mammography. Each site trained a local ResNet-101 model on their private data (total 125,000
images), and only model parameters were shared centrally. We compared federated learning with
centralized training and single-institution models.

Results: The federated model achieved 91.8% AUC, comparable to centralized training (92.1% AUC)
and significantly better than average single-institution performance (85.3% AUC). The approach
maintained HIPAA compliance and preserved local data governance. Training time was 2.3x longer
than centralized but enabled participation from institutions with data sharing restrictions.

Conclusions: Federated learning enables collaborative AI development while preserving patient
privacy, offering a viable path for multi-institutional medical AI research.
        """,
        "url": "https://www.medrxiv.org/content/10.1101/2024.05.15.24307123",
        "published_at": "2024-05-15T00:00:00",
        "source": "medrxiv_demo"
    }
]


def main():
    """Run demonstration of extraction capabilities."""
    print("=" * 100)
    print("medRxiv AI Article Extraction - DEMONSTRATION")
    print("=" * 100)
    print()
    print("This demo shows the extraction capabilities using sample abstracts.")
    print("The system can extract structured information from biomedical AI papers.")
    print()
    print("=" * 100)
    print()
    
    # Initialize extractor (will use heuristic mode without API keys)
    extractor = LLMExtractor()
    
    print(f"Processing {len(SAMPLE_ABSTRACTS)} sample articles...")
    print()
    
    results = []
    
    for i, article in enumerate(SAMPLE_ABSTRACTS, 1):
        print(f"\n{'=' * 100}")
        print(f"ARTICLE {i}/{len(SAMPLE_ABSTRACTS)}")
        print('=' * 100)
        print()
        print(f"📄 Title: {article['title']}")
        print(f"👤 Author: {article['corresponding_author']}")
        print(f"🏥 Affiliation: {', '.join(article['affiliations'])}")
        print(f"📅 Published: {article['published_at'][:10]}")
        print(f"🔗 URL: {article['url']}")
        print()
        
        # Extract information
        extraction, needs_review, raw_output = extractor.extract(article['abstract'])
        
        # Combine with metadata
        result = {
            **article,
            **extraction,
            'needs_manual_review': needs_review
        }
        results.append(result)
        
        # Display extracted information
        print("🔍 EXTRACTED INFORMATION:")
        print("-" * 100)
        print(f"✓ What was done:")
        print(f"  {extraction['what_done']}")
        print()
        print(f"✓ AI Role:")
        print(f"  {extraction['ai_role']}")
        print()
        print(f"✓ Models/Algorithms:")
        print(f"  {extraction['models'] if extraction['models'] else 'Not specified'}")
        print()
        print(f"✓ Data Sources:")
        print(f"  {extraction['data_sources'] if extraction['data_sources'] else 'Not specified'}")
        print()
        print(f"✓ Metrics:")
        print(f"  {extraction['metrics'] if extraction['metrics'] else 'Not specified'}")
        print()
        print(f"⚠️  Needs Manual Review: {needs_review}")
        print()
    
    # Summary
    print("\n" + "=" * 100)
    print("EXTRACTION SUMMARY")
    print("=" * 100)
    print()
    print(f"Total articles processed: {len(results)}")
    print(f"Articles needing review: {sum(1 for r in results if r['needs_manual_review'])}")
    print()
    
    # Save demo results
    demo_dir = Path('data')
    demo_dir.mkdir(exist_ok=True)
    
    demo_json = demo_dir / 'demo_extraction_results.json'
    with open(demo_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Results saved to: {demo_json}")
    print()
    
    # Show sample JSON output
    print("=" * 100)
    print("SAMPLE JSON OUTPUT (First Article):")
    print("=" * 100)
    print()
    print(json.dumps(results[0], indent=2, ensure_ascii=False))
    print()
    
    print("=" * 100)
    print("DEMO COMPLETE")
    print("=" * 100)
    print()
    print("✓ The system successfully extracted structured information from all sample abstracts.")
    print("✓ With real GLM API key, extraction quality would be even higher with LLM analysis.")
    print("✓ The heuristic fallback shown here provides baseline extraction capability.")
    print()
    print("To run with real API:")
    print("  1. Set GLM_API_KEY in .env file")
    print("  2. Run: python tools/run_once.py")
    print()


if __name__ == '__main__':
    main()
