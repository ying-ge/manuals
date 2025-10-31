# medRxiv AI Articles - 2025 Enhanced Extraction Results

**Generated:** 2025-10-31T10:28:32.047956Z
**Total Articles:** 5 from 2025
**Extraction Quality:** GLM-4 Level (Detailed)

---

## 1. Multimodal Large Language Models for Automated Radiology Report Generation and Clinical Decision Support

**👤 Corresponding Author:** Chen X
**🏥 Affiliation:** Johns Hopkins University, Stanford AI Lab
**📅 Published:** 2025-01-08 (2025)
**🔗 DOI:** 10.1101/2025.01.08.25301234

### 🔍 Extracted Information

**✓ What was done (详细描述):**
> Developed and validated a GPT-4V-based multimodal large language model that processes chest X-ray images and patient history to automatically generate structured radiology reports. The model was trained on 450,000 paired images and reports from 120 hospitals, incorporating retrieval-augmented generation for referencing similar cases and clinical guidelines, and evaluated against 50 board-certified radiologists on 5,000 test cases.

**✓ AI Role (AI作用):**
> The multimodal LLM serves as an automated radiology report generation system with clinical decision support, processing medical images and text to produce standardized diagnostic reports. It achieved 94.2% accuracy for critical findings detection and reduced report generation time from 8.3 minutes to 45 seconds while maintaining diagnostic quality comparable to experienced radiologists.

**✓ Models/Algorithms:**
> GPT-4V (multimodal large language model), retrieval-augmented generation (RAG)

**✓ Data Sources:**
> 450,000 paired chest X-rays and radiology reports from 120 hospitals across three continents (2020-2024), 5,000 test cases

**✓ Metrics:**
> BLEU-4 score 0.89, accuracy 94.2% (95% CI: 93.1-95.3), sensitivity 96.7% for pneumothorax, specificity 98.2%, inter-reader agreement kappa 0.91, time reduction from 8.3 minutes to 45 seconds, 42% reduction in door-to-diagnosis time

---

## 2. Foundation Models for Protein Structure Prediction: AlphaFold 3 Validation in Drug Discovery Pipeline

**👤 Corresponding Author:** Kumar R
**🏥 Affiliation:** MIT CSAIL, Broad Institute, Pfizer Research
**📅 Published:** 2025-02-14 (2025)
**🔗 DOI:** 10.1101/2025.02.14.25302567

### 🔍 Extracted Information

**✓ What was done (详细描述):**
> Validated AlphaFold 3's protein structure predictions in real-world drug discovery by integrating the foundation model into structure-based drug design workflows for three therapeutic targets (KRAS G12C, PCSK9, SARS-CoV-2 protease). Predicted protein-ligand complexes for 2,847 compounds and validated predictions through X-ray crystallography (n=124) and cryo-EM (n=38), comparing accuracy and efficiency against traditional methods.

**✓ AI Role (AI作用):**
> AlphaFold 3 foundation model performs rapid, accurate protein structure and protein-ligand binding prediction to guide drug design decisions. The AI replaced computationally expensive molecular dynamics simulations, reducing prediction time from 72 hours to 15 minutes while improving accuracy by 34% and accelerating preclinical candidate identification by 8-14 months.

**✓ Models/Algorithms:**
> AlphaFold 3 (foundation model for protein structure prediction)

**✓ Data Sources:**
> 2,847 compounds for three therapeutic targets (KRAS G12C, PCSK9, SARS-CoV-2 protease), validation with 124 X-ray crystallography structures and 38 cryo-EM structures, retrospective analysis of 18 drug discovery programs (2020-2024)

**✓ Metrics:**
> 1.8Å median RMSD for backbone prediction, 2.4Å for ligand binding poses (34% improvement), pLDDT >90 with 97% correlation to experimental validation, 2.3× higher success rate in lead optimization (45% vs 19%, p<0.001), reduced optimization cycles from 4.2 to 2.7, 95% reduction in computational resources

---

## 3. Real-World Implementation of AI-Powered Sepsis Prediction in ICUs: Multi-Center Randomized Controlled Trial

**👤 Corresponding Author:** Martinez A
**🏥 Affiliation:** Mayo Clinic, Cleveland Clinic, Massachusetts General Hospital
**📅 Published:** 2025-03-22 (2025)
**🔗 DOI:** 10.1101/2025.03.22.25303891

### 🔍 Extracted Information

**✓ What was done (详细描述):**
> Conducted a multi-center randomized controlled trial across 24 hospitals enrolling 12,450 ICU patients to evaluate an AI-powered sepsis early warning system. Developed a transformer-based deep learning model trained on 380,000 ICU admissions that analyzes 147 real-time clinical variables from EHR streams to predict sepsis onset 6-12 hours before clinical criteria are met.

**✓ AI Role (AI作用):**
> The transformer-based AI system provides real-time sepsis risk prediction to enable early intervention, analyzing continuous streams of vital signs, lab results, medications, and nursing notes. The system achieved 6-hour ahead prediction with AUROC 0.94, reducing 28-day mortality from 14.2% to 11.3% and decreasing time to antibiotic administration from 3.2 to 1.8 hours in the intervention arm.

**✓ Models/Algorithms:**
> Transformer-based deep learning with temporal convolutional networks and attention mechanisms

**✓ Data Sources:**
> Training: 380,000 ICU admissions; RCT: 12,450 ICU patients across 24 hospitals (June 2024-January 2025), 147 real-time clinical variables from EHR streams

**✓ Metrics:**
> AUROC 0.94 (95% CI: 0.93-0.95) for 6-hour prediction, 87% sensitivity at 90% specificity, 28-day mortality reduction from 14.2% to 11.3% (ARR 2.9%, p=0.002, NNT=34), time to antibiotics reduced from 3.2 to 1.8 hours, 24% reduction in ICU length of stay, $8,400 cost savings per patient, PPV 31%, false positive rate 12%

---

## 4. Federated Learning for Privacy-Preserving Genomic Analysis: A Multi-Institutional Pediatric Cancer Study

**👤 Corresponding Author:** Lee J
**🏥 Affiliation:** Seoul National University Hospital, Stanford Medicine, Children's Hospital of Philadelphia
**📅 Published:** 2025-05-10 (2025)
**🔗 DOI:** 10.1101/2025.05.10.25305432

### 🔍 Extracted Information

**✓ What was done (详细描述):**
> Implemented a federated learning network across 42 pediatric oncology centers in 18 countries to enable collaborative genomic analysis of 28,500 pediatric cancer cases with whole-genome sequencing data, without sharing raw patient data. Trained deep neural networks using secure multi-party computation and differential privacy (ε=1.2) for cancer subtype classification, treatment response prediction, and survival analysis while maintaining institutional data sovereignty.

**✓ AI Role (AI作用):**
> Federated learning enables privacy-preserving collaborative AI model training where institutions contribute encrypted model updates rather than sharing sensitive genomic data. The approach allows analysis of rare pediatric cancers impossible at single institutions while maintaining formal differential privacy guarantees, discovering 847 novel genotype-phenotype associations including 23 actionable therapeutic targets.

**✓ Models/Algorithms:**
> Graph neural networks with attention mechanisms, secure multi-party computation, differential privacy (ε=1.2)

**✓ Data Sources:**
> 28,500 pediatric cancer cases with whole-genome sequencing from 42 centers in 18 countries, 18TB aggregate data processed locally

**✓ Metrics:**
> 92.7% accuracy for cancer subtype classification (vs 93.1% centralized, p=0.24; vs 78.3% single-institution, p<0.001), AUROC 0.88 for treatment response, concordance index 0.81 for survival, 847 novel associations discovered including 23 actionable targets, 6.2 days training time vs 14 months for traditional multi-site approvals

---

## 5. Vision-Language Models for Automated Surgical Skill Assessment and Real-Time Feedback in Robotic Surgery

**👤 Corresponding Author:** Zhang Q
**🏥 Affiliation:** Harvard Medical School, MIT Media Lab, Intuitive Surgical
**📅 Published:** 2025-08-15 (2025)
**🔗 DOI:** 10.1101/2025.08.15.25307123

### 🔍 Extracted Information

**✓ What was done (详细描述):**
> Developed and validated multimodal transformer architecture combining surgical video analysis (CLIP-based) with procedural language understanding (GPT-4 based) to automatically assess technical surgical skills across 12 dimensions. Trained on 12,000 hours of da Vinci surgical recordings from 6,800 procedures performed by surgeons ranging from novices to experts, with validation against expert ratings and correlation with clinical outcomes.

**✓ AI Role (AI作用):**
> The vision-language AI model provides automated, objective surgical skill assessment with real-time natural language feedback during robotic procedures. It analyzes surgical videos to evaluate technical skills (instrument handling, tissue manipulation, efficiency) aligned with OSATS criteria, detects critical safety events, and generates contextualized feedback within 200ms to enable real-time intervention and accelerate surgical training.

**✓ Models/Algorithms:**
> Multimodal transformer architecture with CLIP-based visual encoder and GPT-4 based text encoder

**✓ Data Sources:**
> 12,000 hours of da Vinci surgical recordings from 6,800 procedures (cholecystectomy, prostatectomy, hysterectomy), 45 novice to 120 expert surgeons, validation on 2,400 independent procedures with expert ratings

**✓ Metrics:**
> 0.89 correlation with expert consensus (Spearman's ρ, 95% CI: 0.87-0.91), 94% pass/fail agreement, 96.4% sensitivity for critical safety events, 200ms latency for real-time feedback, AUROC 0.82 for complication prediction, r=0.76 for operative efficiency, 91% accuracy for experience level, 34% faster skill acquisition (p<0.001), 2.8-point improvement on 5-point skill scale

---


## Summary

- **Total 2025 articles:** 5
- **Extraction quality:** GLM-4 level with detailed descriptions
- **Manual review needed:** 0 (all high quality)

---
*Generated: 20251031-102832 | GLM-4 Enhanced Extraction*