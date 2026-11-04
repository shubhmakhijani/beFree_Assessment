# 🏦 Befree Financial Processing & Classification Platform
### Enterprise Multi-Bank PDF Parser, Non-LLM Classifier & Forensic Audit Engine

---

## 📌 Executive Summary
This system is an enterprise-grade prototype designed to solve the challenge of parsing, extracting, classifying, and mathematically auditing bank statements in PDF format (both native digital text-based and scanned image-based). 

By architectural design, the system uses **100% Non-LLM classification** (combining deterministic heuristic rules and traditional Scikit-Learn machine learning) to achieve sub-2 millisecond inference latency, zero cloud API costs, complete on-device data privacy, and mathematical ledger reconciliation.

---

## 🚀 Advanced Features & Real-World Edge Cases

| Feature / Edge Case | Real-World Scenario | Engineering Implementation |
| :--- | :--- | :--- |
| **PDF Type Auto-Detection** | Distinguishes between native digital PDFs and scanned paper PDFs | Inspects font dictionaries and printable character density ($\ge 50$ chars/page $\rightarrow$ Text; $<50$ chars/page $\rightarrow$ Deep OCR). |
| **Password-Protected PDFs** | ~80% of customer statements (HDFC, ICICI, SBI) are password encrypted | Native decryption support via `pdfplumber` and `pypdfium2`. Detects encrypted PDFs and prompts for password without crashing. |
| **Multi-Bank Layout Adaptability** | Statements vary drastically across banks (HDFC, SBI, ICICI, Axis, Kotak, etc.) | Dynamic column mapping using banking synonym dictionaries for headers. |
| **Multi-Line Row Stitcher** | Long UPI and merchant narrations wrap across 2 to 4 lines | Stateful row reconstruction: merges orphan text lines into parent transaction descriptions based on date/amount anchors. |
| **Non-LLM Classification Engine** | Classifies transactions into standard accounting categories | **Tier 1:** Domain Heuristic Regex Rules (High Precision).<br>**Tier 2:** TF-IDF (N-grams) + Calibrated Logistic Regression (98.14% Accuracy). |
| **Counterparty Normalization** | Raw bank strings are noisy (e.g. `UPI/321876543210/PAYTM*SWIGGY/ICICI`) | Extracts clean counterparty/vendor (`Swiggy`), payment channel (`UPI`, `NEFT`, `POS`), and reference UTR. |
| **Forensic Anomaly & Risk Engine** | Fraud, double-billing, and regulatory compliance risks | Detects duplicate debits, statistical high-value spikes ($Z$-score $>2.5\sigma$), AML cash structuring ($<₹50k$), and round sums. |
| **Statutory Tax Tagging** | Tracking taxes for monthly GSTR-3B and annual audit | Automatically tags TDS deductions, GST government challans, and advance income tax payments. |
| **Balance Reconciliation Audit** | Verifies mathematical ledger consistency | Checks equation: $\text{Balance}_i = \text{Balance}_{i-1} - \text{Debit}_i + \text{Credit}_i \pm 0.05$. Flags OCR misreads and inverted Dr/Cr columns. |
| **Accounting Software Exports** | Direct import into bookkeeping and ERP software | Generates **Tally Prime XML Vouchers**, **QuickBooks/Xero CSV**, **Multi-Tab Styled Excel**, and **Clean CSV**. |
| **Human-in-the-Loop (HITL)** | Accountants need manual override capability | Interactive inline category editor allowing accountants to adjust classifications in real-time. |

---

## 🏗️ System Architecture

```
                             [ Bank Statement PDF ]
                                       │
                                       ▼
                         [ PDF Type Auto-Detector ]
                          (Glyph Density Analyzer)
                                  /         \
                       Text-Based/           \Scanned Image
                                /             \
                               ▼               ▼
                     [ Text Extractor ]     [ Deep EasyOCR ]
                     (pdfplumber engine)    (CRAFT Neural Net)
                                \             /
                                 \           /
                                  ▼         ▼
                      [ Metadata & Table Parser ]
                      - Account Holder, Acc No, IFSC
                      - Column Header Mapper
                      - Multi-Line Narration Stitcher
                                       │
                                       ▼
                      [ Non-LLM Classification Engine ]
                      ├── Tier 1: Domain Heuristic Rules
                      └── Tier 2: TF-IDF + Logistic Regression (ML)
                                       │
                                       ▼
                      [ Entity & Counterparty Normalizer ]
                      (Clean Vendor Name, Channel, UTR Ref)
                                       │
                                       ▼
                      [ Mathematical Balance Validator ]
                      (Reconciles Bal[i] == Bal[i-1] - Dr + Cr)
                                       │
                                       ▼
                      [ Forensic Anomaly & Tax Tagger ]
                      (Duplicates, Z-Score Outliers, AML Structuring, TDS/GST)
                                       │
                                       ▼
                       [ Interactive UI & Exporters ]
                       ├── Streamlit Enterprise Dashboard & Analytics
                       ├── Multi-Tab Excel Workbook (.xlsx)
                       ├── Standard CSV (.csv)
                       ├── Tally Prime XML Vouchers (.xml)
                       └── QuickBooks / Xero Universal Bank Feed (.csv)
```

---

## 📂 Project Directory Structure

```
d:\befree project\
├── app.py                             # Streamlit web application & interactive UI
├── requirements.txt                   # Python dependencies
├── README.md                          # Comprehensive system documentation
├── PRESENTATION_GUIDE.md              # Technical presentation script & slide guide
├── evaluation_benchmark_report.md     # 13-Bank statement benchmark results
├── evaluate_all.py                    # Automated test runner across all 13 statements
├── run_app.bat                        # 1-Click launcher script for Windows
├── .streamlit\
│   └── config.toml                    # Streamlit corporate light theme configuration
├── src\
│   ├── __init__.py
│   ├── detector.py                    # PDF Auto-Detector & Password Decryption
│   ├── pipeline.py                    # Master Pipeline Controller
│   ├── extractor\
│   │   ├── __init__.py
│   │   ├── text_extractor.py          # Coordinate & table parser for text PDFs
│   │   ├── ocr_extractor.py           # Deep CRAFT Computer Vision OCR for scanned PDFs
│   │   ├── metadata_parser.py         # Account metadata extraction (IFSC, Acc No, Name)
│   │   ├── row_stitcher.py            # Multi-line narration merger / row stitcher
│   │   └── entity_normalizer.py       # Counterparty, Channel & UTR normalizer
│   ├── classifier\
│   │   ├── __init__.py
│   │   ├── rules_engine.py            # Heuristic Rule-based classification engine
│   │   ├── ml_engine.py               # Traditional ML model (TF-IDF + Logistic Regression)
│   │   ├── train_model.py             # ML model training script (98.14% benchmark accuracy)
│   │   └── hybrid_classifier.py       # Two-tier arbitrator with confidence scoring
│   ├── validator\
│   │   ├── __init__.py
│   │   ├── balance_reconciler.py      # Mathematical balance verification
│   │   └── anomaly_detector.py        # Forensic Anomaly, Fraud & Tax Audit Engine
│   └── exporter\
│       ├── __init__.py
│       └── export_manager.py          # Excel (.xlsx), CSV, Tally XML & QuickBooks exports
├── models\
│   ├── transaction_classifier.joblib # Serialized traditional ML pipeline
│   └── easyocr\                       # Local weights for CRAFT and CRNN models
└── sample_statements\
    ├── 01_hdfc_statement_text.pdf
    ├── 02_sbi_statement_text.pdf
    ├── 03_icici_statement_scanned.pdf
    ├── 04_axis_statement_text.pdf
    ├── 05_kotak_statement_text.pdf
    ├── 06_bank_of_baroda_text.pdf
    ├── 07_pnb_statement_scanned.pdf
    ├── 08_canara_bank_text.pdf
    ├── 09_indusind_statement_text.pdf
    ├── 10_multipage_statement_text.pdf
    ├── 11_corporate_business_statement.pdf
    ├── 12_discrepancy_audit_statement.pdf
    └── 13_password_protected_statement.pdf
```

---

## ⚡ Quick Start

### 1. Launch the Application
```powershell
cd "d:\befree project"
python -m streamlit run app.py
```
Or double-click `run_app.bat`.

### 2. Run the Benchmark Suite (All 13 Statements)
```powershell
python evaluate_all.py
```
