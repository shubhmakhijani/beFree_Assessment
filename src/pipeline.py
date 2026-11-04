import io
from typing import Dict, Any, Union, Optional
from src.detector import PDFTypeDetector
from src.extractor.text_extractor import TextBasedExtractor
from src.extractor.ocr_extractor import OCRExtractor
from src.extractor.entity_normalizer import EntityNormalizer
from src.classifier.hybrid_classifier import HybridTransactionClassifier
from src.validator.balance_reconciler import BalanceReconciler
from src.validator.anomaly_detector import ForensicAnomalyDetector
from src.exporter.export_manager import ExportManager


class BankStatementPipeline:
    """
    End-to-End Enterprise Orchestrator for the Bank Statement Processing & Classification System.
    Incorporates:
      - Encrypted / Password-Protected Statement Decryption
      - Glyph Density PDF Type Auto-Detection (Text vs Scanned)
      - Dual Extraction (Coordinate Tables vs Deep CRAFT Computer Vision)
      - Stateful Multi-Line Remark Stitching
      - Non-LLM Hybrid Classification (Heuristic Rules + Scikit-Learn TF-IDF Logistic Regression)
      - Accounting Entity Normalization (Counterparty, Channel, Reference UTR)
      - Double-Entry Mathematical Balance Reconciliation
      - Forensic Anomaly, Fraud & Tax Audit Engine
      - Accounting Exports (Styled Excel, CSV, Tally Prime XML, QuickBooks/Xero CSV)
    """

    @classmethod
    def process_statement(
        cls, 
        file_source: Union[str, bytes, io.BytesIO],
        file_name: str = "statement.pdf",
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the entire ingestion, detection, extraction, classification,
        validation, and export generation workflow.
        """
        # Read bytes once so they can be passed to multiple components safely
        if isinstance(file_source, bytes):
            pdf_bytes = file_source
        elif isinstance(file_source, io.BytesIO):
            pdf_bytes = file_source.getvalue()
        elif isinstance(file_source, str):
            with open(file_source, "rb") as f:
                pdf_bytes = f.read()
        else:
            if hasattr(file_source, "read"):
                curr = file_source.tell() if hasattr(file_source, "tell") else 0
                pdf_bytes = file_source.read()
                if hasattr(file_source, "seek"):
                    file_source.seek(curr)
            else:
                raise ValueError("Unsupported input format")

        # 1. Auto-Detection (Text vs Image/Scanned vs Password-Protected)
        detection_result = PDFTypeDetector.detect(pdf_bytes, password=password)
        doc_type = detection_result["doc_type"]

        if doc_type == "PASSWORD_PROTECTED":
            return {
                "status": "PASSWORD_REQUIRED",
                "file_name": file_name,
                "error_message": "Statement is encrypted with a password. Please enter the password to unlock.",
                "detection": detection_result,
                "metadata": {},
                "transactions": [],
                "reconciliation": {
                    "total_transactions": 0,
                    "reconciliation_status": "PASSWORD_REQUIRED",
                    "integrity_score": 0.0,
                    "discrepancy_count": 0,
                    "total_debits": 0.0,
                    "total_credits": 0.0,
                    "net_change": 0.0
                },
                "anomalies": {
                    "risk_profile": "UNKNOWN",
                    "total_flagged": 0,
                    "duplicates_count": 0,
                    "outliers_count": 0,
                    "structuring_count": 0,
                    "tax_events_count": 0
                },
                "extraction_stats": {},
                "exports": {
                    "csv": "",
                    "excel": b"",
                    "tally_xml": "",
                    "quickbooks_csv": ""
                }
            }

        # 2. Routing to Extraction Engine
        if doc_type == "TEXT_BASED":
            extraction_result = TextBasedExtractor.extract(pdf_bytes, password=password)
        else:
            extraction_result = OCRExtractor.extract(pdf_bytes)

        metadata = extraction_result["metadata"]
        raw_txns = extraction_result["transactions"]

        # 3. Non-LLM Transaction Classification (Heuristic + Traditional ML)
        classified_txns = HybridTransactionClassifier.classify_all(raw_txns)

        # 4. Accounting Counterparty & Channel Normalization
        normalized_txns = EntityNormalizer.normalize_transactions(classified_txns)

        # 5. Mathematical Balance Reconciliation & Integrity Validation
        reconciled_txns, reconciliation_summary = BalanceReconciler.reconcile(normalized_txns)

        # 6. Forensic Anomaly & Audit Risk Engine
        final_txns, anomaly_summary = ForensicAnomalyDetector.analyze(reconciled_txns)

        # 7. Multi-Format Accounting Exports
        csv_data = ExportManager.to_csv(final_txns)
        excel_bytes = ExportManager.to_excel_bytes(final_txns, metadata, reconciliation_summary, anomaly_summary)
        tally_xml_data = ExportManager.to_tally_xml(final_txns, metadata)
        qb_csv_data = ExportManager.to_quickbooks_csv(final_txns)

        return {
            "status": "SUCCESS",
            "file_name": file_name,
            "detection": detection_result,
            "metadata": metadata,
            "transactions": final_txns,
            "reconciliation": reconciliation_summary,
            "anomalies": anomaly_summary,
            "extraction_stats": extraction_result["extraction_stats"],
            "exports": {
                "csv": csv_data,
                "excel": excel_bytes,
                "tally_xml": tally_xml_data,
                "quickbooks_csv": qb_csv_data
            }
        }
