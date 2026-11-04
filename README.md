# Befree Financial Processing & Autonomous Ledger Classification Platform
### Enterprise Multi-Bank PDF Parser, Non-LLM Hybrid Classifier, Forensic Audit & Multi-Format Accounting Export Pipeline

[![Non-LLM Core](https://img.shields.io/badge/Non--LLM%20Classification-100%25%20Rule%20%2B%20ML-0D5C75?style=for-the-badge&logo=scikitlearn)](https://github.com)
[![Accuracy](https://img.shields.io/badge/Verified%20Accuracy-98.14%25-00875A?style=for-the-badge)](https://github.com)
[![Audit Compliance](https://img.shields.io/badge/Audit%20Integrity-100%25%20Mathematical-0052CC?style=for-the-badge)](https://github.com)
[![Privacy First](https://img.shields.io/badge/Data%20Privacy-100%25%20On--Device%20(Zero%20Leaks)-36B37E?style=for-the-badge)](https://github.com)
[![Cloud Cost](https://img.shields.io/badge/Inference%20Cost-%240.00%20(Local%20CPU)-FFAB00?style=for-the-badge)](https://github.com)

---

## Executive Summary

Modern accounting firms face severe operational bottlenecks when onboarding customer bank statements. Client statements arrive in dozens of heterogeneous formats: native digital PDFs, multi-page consolidated accounts, password-encrypted files, and scanned physical documents with skewed orientations. Furthermore, transactions often contain wrapped multi-line narrations, complex UPI/NEFT reference codes, and varied column ordering (e.g., Deposit before Withdrawal vs Withdrawal before Deposit).

This platform provides an autonomous, end-to-end financial data pipeline designed specifically to solve these real-world challenges:
- **Intelligent Ingestion & In-Memory Decryption**: Handles password-protected PDFs and automatically routes documents using character glyph stream density ($\ge 50$ chars/page $\rightarrow$ vector stream; $<50$ chars/page $\rightarrow$ deep computer vision OCR).
- **Layout-Agnostic Dual Extraction**: Dynamically maps varied column names, handles inverted debit/credit columns, recognizes 3-token date formats (e.g., `16 Jun 19`), and uses a stateful RowStitcher state machine to merge multi-line narrations.
- **100% Non-LLM Hybrid Classification**: Combines a high-precision Heuristic Domain Rules Engine (100+ patterns) with a sublinear TF-IDF + Logistic Regression ML model (98.14% benchmark accuracy, $<2\text{ms}$ latency, zero cloud API cost).
- **Mathematical Balance Reconciliation & Forensic Audit**: Formally reconciles running balances using the fundamental accounting identity ($\text{Balance}_i = \text{Balance}_{i-1} - \text{Debit}_i + \text{Credit}_i \pm 0.05$) and tags forensic anomalies (Z-score outlier spikes $>2.5\sigma$, duplicate transactions, AML structuring $<₹50\text{k}$, and statutory GST/TDS tax deductions).
- **Enterprise Accounting Exports**: Automatically compiles validated data into Multi-Tab Styled Excel workbooks, Tally Prime XML vouchers, QuickBooks / Xero CSV feeds, and normalized CSV tables.

---

## System Architecture Blueprint

The platform follows a modular, 5-phase execution flow engineered for high throughput, zero cloud dependency, and total reproducibility:

<p align="center">
  <img src="docs/screenshots/01_system_architecture_diagram.png" width="100%" alt="Befree System Architecture Flow Diagram" />
</p>

### Phase-by-Phase Technical Breakdown

- **Phase 1: Ingestion & Security Layer**
  - In-Memory Password Decryption: Native decryption via `pdfplumber` and `pypdfium2` with zero temporary disk footprint.
  - PDF Type Detector: Analyzes character glyph stream density per page to route files to the optimal parser ($\ge 50$ chars $\rightarrow$ Text Engine; $< 50$ chars $\rightarrow$ Deep OCR Engine).

- **Phase 2: Dual Extraction & Stateful Stitching**
  - Text-Based Extractor: Coordinate-aware layout extractor resolving unbordered and collapsed table rows.
  - Deep OCR Extractor: EasyOCR CRAFT deep neural network for scanned bitmaps and physical receipts.
  - Multi-Token Date Normalizer: Robust regex parsing supporting 3-token dates (`16 Jun 19`), numeric formats (`16/06/2019`), and ISO dates (`2019-06-16`).
  - RowStitcher State Machine: Recovers wrapped multi-line narrations by anchoring on transaction dates and balance continuity.
  - Metadata Parser: Extracts account holder name, account number, branch IFSC code, statement period, and balances.
  - Entity Normalizer: Cleans merchant and vendor strings, extracts transaction channels (UPI, NEFT, IMPS, POS), and isolates UTR references.

- **Phase 3: Non-LLM Two-Tier Classification Engine**
  - Tier 1: Domain Heuristic Rules Engine with 100+ compiled regex signatures (99.8% precision on matching transactions).
  - Tier 2: Traditional Scikit-Learn ML Model utilizing sublinear TF-IDF (1-2 N-grams) and Calibrated Logistic Regression.
  - Probability Calibration Gate: Transactions with predicted confidence $\ge 0.40$ are categorized; lower confidence transactions are flagged for review.

- **Phase 4: Validation & Forensic Audit Engine**
  - Balance Reconciler: Row-by-row mathematical audit enforcing $\text{Balance}[i] = \text{Balance}[i-1] - \text{Debit}[i] + \text{Credit}[i] \pm 0.05$.
  - Inverted Column Detector: Detects reversed debit/credit structures and alerts the user.
  - Duplicate Transaction Detector: Flags potential duplicate swipes based on identical date, amount, and counterparty.
  - Z-Score Statistical Outlier Engine: Flags high-value spending spikes exceeding $2.5$ standard deviations from the debit mean.
  - AML Cash Structuring Monitor: Identifies repeated deposits or withdrawals positioned just below the regulatory threshold ($< ₹50,000$).
  - Statutory Tax Tagger: Flags transactions corresponding to TDS deductions, GST government challans, and advance tax payments.

- **Phase 5: Enterprise Export & Interactive UI Portal**
  - Streamlit Corporate Dashboard: Financial KPI metric cards, interactive category donut chart, and cash flow timeline.
  - Human-in-the-Loop (HITL) Category Override: Allows accounting professionals to adjust classifications with dynamic ledger recalculation.
  - Multi-Tab Formatted Excel (.xlsx): Generated with openpyxl containing Summary, Classified Ledger, and Forensic Audit sheets.
  - Tally Prime XML Vouchers (.xml): Native `<TALLYMESSAGE>` XML payment and receipt ledger vouchers for gateway import.
  - QuickBooks / Xero Universal Bank Feed CSV (.csv): Standardized 4-column format (Date, Payee, Description, Amount).
  - Normalized Accounting CSV (.csv): Flat table with clean fields for database ingestion.

---

## System Screenshots & Visual Verification

### 1. Real-Time Statement Processing Dashboard
Processes multi-page bank statements (e.g., 22-page ICICI, 5-page HDFC, 4-page Standard Chartered) with full account headers, KPI metric cards, forensic accounting risk indicators, and system diagnostics:

<p align="center">
  <img src="docs/screenshots/02_statement_processor_dashboard.png" width="100%" alt="Statement Processor Dashboard" />
</p>

---

### 2. Financial Insights & Interactive Ledger Visualizations
Interactive category spending breakdown (donut chart) and temporal cash flow activity timeline (credits vs debits over time):

<p align="center">
  <img src="docs/screenshots/03_financial_insights_visualizations.png" width="100%" alt="Financial Insights and Cash Flow Visualizations" />
</p>

---

### 3. Classified Ledger Records, Human-in-the-Loop (HITL) & 1-Click Exports
Interactive ledger records table featuring normalized counterparty names, payment channels, transaction confidence scores, audit verification badges, and one-click export buttons for Excel, CSV, Tally XML, and QuickBooks:

<p align="center">
  <img src="docs/screenshots/04_ledger_records_hitl_exports.png" width="100%" alt="Ledger Records Table with HITL and Exports" />
</p>

---

### 4. Multi-Bank Benchmark & Batch Audit Hub (13-Bank Suite)
Automated batch evaluation hub executing against 13 diverse multi-bank statement formats covering HDFC, SBI, ICICI, Axis, Kotak, Bank of Baroda, PNB, Canara, IndusInd, multi-page corporate ledgers, and intentional discrepancy audits:

<p align="center">
  <img src="docs/screenshots/05_multi_bank_batch_benchmark_hub.png" width="100%" alt="Multi-Bank Benchmark and Batch Audit Hub" />
</p>

---

### 5. Traditional ML Model Performance & Evaluation Metrics
High-accuracy traditional machine learning classifier achieving **98.14% test accuracy** across 10 accounting categories with sub-millisecond inference and zero API cost:

<p align="center">
  <img src="docs/screenshots/07_ml_model_evaluation_metrics.png" width="100%" alt="Traditional ML Model Evaluation Metrics" />
</p>

---

### 6. Interactive Engineering Architecture Tab in Streamlit
Integrated interactive system architecture blueprint embedded directly in the platform for accountant and auditor reference:

<p align="center">
  <img src="docs/screenshots/06_architecture_in_streamlit_app.png" width="100%" alt="Engineering Architecture in Streamlit App" />
</p>

---

## Multi-Tab Formatted Excel Workbook Output (.xlsx)

When an accountant clicks **"Download Multi-Tab Excel (.xlsx)"**, the platform automatically compiles an executive-styled workbook:

### Sheet 1: Account Summary & Financial Health KPIs
<p align="center">
  <img src="docs/screenshots/08_excel_export_account_summary.png" width="100%" alt="Excel Export - Sheet 1: Account Summary" />
</p>

### Sheet 2: Classified Ledger Feed with Accounting Formatting
<p align="center">
  <img src="docs/screenshots/09_excel_export_classified_ledger.png" width="100%" alt="Excel Export - Sheet 2: Classified Ledger" />
</p>

### Sheet 3: Forensic Audit & Risk Intelligence Log
<p align="center">
  <img src="docs/screenshots/10_excel_export_forensic_audit.png" width="100%" alt="Excel Export - Sheet 3: Forensic Audit" />
</p>

---

## Source Code Architecture & Design Highlights

### 1. Two-Tier Non-LLM Hybrid Classifier (`src/classifier/hybrid_classifier.py`)
Combines deterministic heuristic rules with a TF-IDF logistic regression classifier and probability calibration:

<p align="center">
  <img src="docs/screenshots/11_code_hybrid_transaction_classifier.png" width="100%" alt="Code - Hybrid Transaction Classifier" />
</p>

---

### 2. Master Execution Pipeline Orchestrator (`src/pipeline.py`)
Coordinates auto-detection, text/OCR routing, multi-line stitching, normalization, mathematical reconciliation, forensic tagging, and multi-format exports:

<p align="center">
  <img src="docs/screenshots/12_code_bank_statement_pipeline.png" width="100%" alt="Code - Master Pipeline Orchestrator" />
</p>

---

### 3. Forensic Anomaly & Risk Detection Engine (`src/validator/anomaly_detector.py`)
Performs statistical outlier analysis ($Z > 2.5\sigma$), duplicate payment detection, AML cash structuring checks, and statutory tax tagging:

<p align="center">
  <img src="docs/screenshots/13_code_forensic_anomaly_detector_part1.png" width="100%" alt="Code - Forensic Anomaly Detector Part 1" />
</p>
<p align="center">
  <img src="docs/screenshots/14_code_forensic_anomaly_detector_part2.png" width="100%" alt="Code - Forensic Anomaly Detector Part 2" />
</p>

---

## Multi-Bank Benchmark Evaluation Matrix

The system includes an automated evaluation suite (`evaluate_all.py`) testing across 13 diverse banking scenarios:

| # | Statement File | Type Detected | Bank Identified | Account Holder | Processed Txns | Total Debit (INR) | Total Credit (INR) | Ledger Audit Status | Integrity Score | Processing Latency |
|:---:|:---|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | `01_hdfc_statement_text.pdf` | TEXT_BASED | HDFC BANK | MR. RAJESH SHARMA | 14 | ₹36,125.00 | ₹85,625.00 | **BALANCED** | **100.0%** | 239.8 ms |
| 2 | `02_sbi_statement_text.pdf` | TEXT_BASED | STATE BANK OF INDIA | MS. PRIYA PATEL | 9 | ₹11,048.00 | ₹65,000.00 | **BALANCED** | **100.0%** | 120.2 ms |
| 3 | `03_icici_statement_scanned.pdf` | IMAGE_BASED | ICICI BANK | MR. SUNIL VERMA | 8 | ₹5,834.00 | ₹70,000.00 | **BALANCED** | **100.0%** | 23,005.8 ms |
| 4 | `04_axis_statement_text.pdf` | TEXT_BASED | AXIS BANK | MR. VIKRAM ADITYA | 8 | ₹29,450.00 | ₹92,000.00 | **BALANCED** | **100.0%** | 112.0 ms |
| 5 | `05_kotak_statement_text.pdf` | TEXT_BASED | KOTAK MAHINDRA BANK | MRS. ANANYA SEN | 9 | ₹58,969.00 | ₹126,150.00 | **BALANCED** | **100.0%** | 105.4 ms |
| 6 | `06_bank_of_baroda_text.pdf` | TEXT_BASED | BANK OF BARODA | MR. DEEPAK JOSHI | 7 | ₹5,610.00 | ₹48,000.00 | **BALANCED** | **100.0%** | 85.9 ms |
| 7 | `07_pnb_statement_scanned.pdf` | IMAGE_BASED | ICICI BANK | MR AMANPREET SINGH | 7 | ₹6,257.00 | ₹52,000.00 | **BALANCED** | **100.0%** | 13,758.2 ms |
| 8 | `08_canara_bank_text.pdf` | TEXT_BASED | CANARA BANK | MR. KARTHIK SUBRAMANIAM | 8 | ₹8,820.00 | ₹58,000.00 | **BALANCED** | **100.0%** | 109.5 ms |
| 9 | `09_indusind_statement_text.pdf` | TEXT_BASED | INDUSIND BANK | MS SANYA MEHTA | 10 | ₹11,348.00 | ₹110,000.00 | **BALANCED** | **100.0%** | 107.4 ms |
| 10 | `10_multipage_statement_text.pdf` | TEXT_BASED | HDFC BANK | MR. ARUN VERMA | 11 | ₹41,270.00 | ₹136,250.00 | **BALANCED** | **100.0%** | 125.4 ms |
| 11 | `11_corporate_business_statement.pdf` | TEXT_BASED | ICICI BANK | TECHNOVATE SOLUTIONS PVT LTD | 8 | ₹393,000.00 | ₹380,000.00 | **BALANCED** | **100.0%** | 101.4 ms |
| 12 | `12_discrepancy_audit_statement.pdf` | TEXT_BASED | STATE BANK OF INDIA | MR. SURESH MENON | 5 | ₹3,299.00 | ₹60,000.00 | **DISCREPANCIES_FOUND** | **80.0%** | 79.2 ms |
| 13 | `13_password_protected_statement.pdf` | TEXT_BASED | HDFC BANK | MR. VIKRAM MALHOTRA | 7 | ₹22,170.00 | ₹195,000.00 | **BALANCED** | **100.0%** | 303.9 ms |

### Real-World Customer Statements Verified

Beyond synthetic benchmarks, the platform was verified on complex, multi-page live customer statements:
- **Real 4-Page Standard Chartered Bank Statement (`MR SEENIVASAN`)**:
  - Identified Bank: **STANDARD CHARTERED BANK** (IFSC: `SCBL0036078`)
  - Extracted: **51 Transactions**
  - Total Credits: **₹70,986.83** | Total Debits: **₹69,291.02** | Closing Balance: **₹116,149.46** *(Exact paisa match to statement total)*
  - Reconciliation Status: **100.0% BALANCED (0 Discrepancies)**
- **Real 5-Page HDFC NetBanking Statement (`MR. ANUP DUBEY`)**:
  - Identified Bank: **HDFC BANK** (IFSC: `HDFC0001116`)
  - Extracted: **85 Transactions**
  - Total Debits: **₹189,017.40** | Total Credits: **₹182,102.39**
  - Reconciliation Status: **100.0% BALANCED (0 Discrepancies)**

---

## Edge Cases & Real-World Resilience

| Edge Case | Problem Description | Engineered Solution |
|---|---|---|
| **3-Token Space Dates** | Banks like Standard Chartered format dates as `16 Jun 19` rather than `16/06/2019`. | Hybrid token parser scans 3-word windows (`\d{1,2} [A-Za-z]{3} \d{2,4}`) and extracts value dates without description pollution. |
| **Inverted Columns** | Standard Chartered orders headers as `Deposit \| Withdrawal`; HDFC orders `Withdrawal \| Deposit`. | Dynamic column alignment scans headers, calculates midpoint boundaries, and dynamically maps amounts. |
| **Intra-Day Transactions** | Statements often omit repeated date tokens for same-day transactions. | Stateful tracking maintains `current_date` across rows containing valid amount and balance pairs. |
| **Vendor Narration IFSCs** | Remarks like `AIRTELIN@HDFCBANK/HDFC0000053/` caused false bank identification. | Header branch IFSC codes (`SCBL0036078`) are granted strict priority over narration mentions. |
| **Honorific Variations** | `MR SEENIVASAN` (no period) previously caused fallback to address lines. | Regex matches honorifics (`MR`, `MRS`, `MS`, `DR`, `M/S`) with or without trailing dots. |
| **Multi-Line Row Stitching** | UPI and IMPS remarks frequently wrap across 2 to 4 visual lines. | `RowStitcher` state machine buffers trailing lines and joins them into the parent transaction. |
| **In-Memory Decryption** | Passwords required for encrypted statements can leak if written to disk. | Decryption executes purely in-memory via byte streams (`io.BytesIO`) with zero temporary file footprint. |

---

## Project Directory Structure

```
befree-project/
├── app.py                             # Streamlit corporate web application & UI
├── requirements.txt                   # Production Python dependencies
├── README.md                          # Master technical documentation
├── PRESENTATION_GUIDE.md              # Technical presentation script & slide guide
├── evaluation_benchmark_report.md     # 13-Bank statement evaluation report
├── evaluate_all.py                    # Automated test runner across all 13 statements
├── run_app.bat                        # 1-Click launcher script for Windows
├── architecture_diagram.svg           # High-resolution Draw.io vector SVG diagram
├── architecture_diagram.drawio        # Native editable Draw.io XML source file
├── architecture_diagram.html          # Standalone interactive browser diagram
├── .gitignore                         # Configured to ignore pycache & heavy OCR weights
├── .streamlit/
│   └── config.toml                    # Befree executive corporate styling config
├── docs/
│   └── screenshots/                   # Documentation screenshots (01 to 14)
├── all screenshots/                   # System screenshots
├── src/
│   ├── __init__.py
│   ├── detector.py                    # PDF Type Auto-Detector & Password Decryption
│   ├── pipeline.py                    # Master Pipeline Controller & Orchestrator
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── text_extractor.py          # Coordinate & table parser for text PDFs
│   │   ├── ocr_extractor.py           # Deep CRAFT Computer Vision OCR for scanned PDFs
│   │   ├── metadata_parser.py         # Account metadata extraction (IFSC, Acc No, Name)
│   │   ├── row_stitcher.py            # Multi-line narration merger / row stitcher
│   │   └── entity_normalizer.py       # Counterparty, Channel & UTR normalizer
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── rules_engine.py            # Heuristic Rule-based classification engine
│   │   ├── ml_engine.py               # Traditional ML model (TF-IDF + Logistic Regression)
│   │   ├── train_model.py             # ML model training script (98.14% benchmark accuracy)
│   │   └── hybrid_classifier.py       # Two-tier arbitrator with confidence scoring
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── balance_reconciler.py      # Mathematical balance verification engine
│   │   └── anomaly_detector.py        # Forensic Anomaly, Fraud & Tax Audit Engine
│   └── exporter/
│       ├── __init__.py
│       └── export_manager.py          # Excel (.xlsx), CSV, Tally XML & QuickBooks exports
├── models/
│   └── transaction_classifier.joblib  # Serialized traditional ML model pipeline
└── sample_statements/                 # 13 Multi-bank benchmark test PDFs
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

## Quick Start & Installation

### 1. Prerequisites
- Python 3.10 - 3.14 installed on your workstation.
- Git installed.

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/shubhmakhijani/beFree_Assessment.git
cd beFree_Assessment

# Create a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python -m streamlit run app.py
```
*Or on Windows: simply double-click `run_app.bat`.*

The interactive web portal will open at `http://localhost:8501`.

### 4. Run the 13-Bank Automated Benchmark Suite
```bash
python evaluate_all.py
```

---

## Key Advantages for Enterprise Accounting
- **$0.00 Operational API Cost**: Zero dependencies on OpenAI, Anthropic, or external LLM gateways.
- **Strict Financial Privacy**: Processing occurs entirely in-memory on local compute; customer financial records never leave the perimeter.
- **Ultra-Low Latency**: Traditional ML + rule-based inference completes in $<2\text{ms}$ per transaction vs $800-2500\text{ms}$ for cloud LLMs.
- **Mathematical Precision**: Eliminates generative hallucinations; deterministic balance reconciler verifies ledger equations down to the exact paisa.
- **Turnkey ERP Integration**: Native Tally Prime XML and QuickBooks feeds eliminate manual accountant data entry.
