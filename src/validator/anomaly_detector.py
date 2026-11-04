import math
import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class ForensicAnomalyDetector:
    """
    Forensic Accounting & Anomaly Detection Engine:
    Identifies high-risk transactions, accidental double-billing, 
    regulatory structuring alerts, high-value statistical outliers, 
    and statutory tax deductions across bank statement ledgers.
    """

    ROUND_NUM_THRESHOLD = 25000.0
    STRUCTURING_BANDS = [
        (47000.0, 49999.0),  # Under INR 50k PAN reporting limit
        (9000.0, 9999.0)     # Under INR 10k cash limit
    ]

    TAX_PATTERNS = {
        "TDS": re.compile(r"\b(TDS|TAX\s*DED|T\.D\.S|194[A-J]|WITHHOLDING\s*TAX)\b", re.IGNORECASE),
        "GST": re.compile(r"\b(GST|GSTPMT|CPIN|CIN|GOODS\s*AND\s*SERVICES\s*TAX|GSTR)\b", re.IGNORECASE),
        "ADVANCE_TAX": re.compile(r"\b(CHALLAN\s*280|ADVANCE\s*TAX|SELF\s*ASSESSMENT|CBDT|INCOME\s*TAX)\b", re.IGNORECASE)
    }

    @classmethod
    def analyze(cls, transactions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Runs forensic multi-pass audit across all transactions.
        
        Returns:
            - transactions: enhanced with 'anomaly_flags', 'risk_level', and 'tax_tag'
            - summary: forensic audit telemetry report
        """
        if not transactions:
            return [], {
                "risk_profile": "LOW",
                "total_flagged": 0,
                "duplicates_count": 0,
                "outliers_count": 0,
                "structuring_count": 0,
                "tax_events_count": 0,
                "details": []
            }

        analyzed = []
        debit_amounts = [float(t.get("debit", 0.0) or 0.0) for t in transactions if float(t.get("debit", 0.0) or 0.0) > 0]
        
        # Calculate statistics for Z-score outlier detection
        n_debits = len(debit_amounts)
        if n_debits >= 3:
            mean_debit = sum(debit_amounts) / n_debits
            variance = sum((x - mean_debit) ** 2 for x in debit_amounts) / n_debits
            std_debit = math.sqrt(variance)
            outlier_cutoff = mean_debit + (2.5 * std_debit)
        else:
            mean_debit = 0.0
            outlier_cutoff = float("inf")

        # Track duplicates by (date, amount, type)
        seen_txns = defaultdict(list)
        for i, t in enumerate(transactions):
            d = t.get("date", "")
            amt = float(t.get("debit", 0.0) or 0.0) or float(t.get("credit", 0.0) or 0.0)
            is_dr = float(t.get("debit", 0.0) or 0.0) > 0
            if amt > 0:
                seen_txns[(d, amt, is_dr)].append(i)

        duplicates_count = 0
        outliers_count = 0
        structuring_count = 0
        tax_events_count = 0

        for i, t in enumerate(transactions):
            row = dict(t)
            flags = []
            risk_level = "LOW"
            tax_tag = None
            desc = str(row.get("description", ""))
            debit = float(row.get("debit", 0.0) or 0.0)
            credit = float(row.get("credit", 0.0) or 0.0)
            amt = debit if debit > 0 else credit
            is_dr = debit > 0

            # 1. Duplicate Transaction Detection
            d_key = (row.get("date", ""), amt, is_dr)
            if len(seen_txns[d_key]) > 1:
                flags.append("POTENTIAL_DUPLICATE")
                risk_level = "MEDIUM"
                duplicates_count += 1

            # 2. High-Value Statistical Outlier
            if is_dr and debit >= outlier_cutoff and debit >= 25000.0:
                flags.append("STATISTICAL_OUTLIER_SPIKE")
                risk_level = "HIGH" if risk_level != "CRITICAL" else risk_level
                outliers_count += 1

            # 3. Regulatory Cash Structuring / Smurfing Threshold Check
            for lower_bound, upper_bound in cls.STRUCTURING_BANDS:
                if lower_bound <= amt <= upper_bound:
                    flags.append("REGULATORY_THRESHOLD_PROXIMITY")
                    if risk_level == "LOW":
                        risk_level = "MEDIUM"
                    structuring_count += 1
                    break

            # 4. Significant Round Sum Transaction Flag
            if amt >= cls.ROUND_NUM_THRESHOLD and amt % 5000 == 0:
                flags.append("ROUND_SUM_TRANSACTION")

            # 5. Statutory Tax Tagging
            if cls.TAX_PATTERNS["TDS"].search(desc):
                tax_tag = "TDS_DEDUCTION"
                flags.append("TAX_EVENT")
                tax_events_count += 1
            elif cls.TAX_PATTERNS["GST"].search(desc):
                tax_tag = "GST_PAYMENT"
                flags.append("TAX_EVENT")
                tax_events_count += 1
            elif cls.TAX_PATTERNS["ADVANCE_TAX"].search(desc):
                tax_tag = "ADVANCE_INCOME_TAX"
                flags.append("TAX_EVENT")
                tax_events_count += 1

            # If arithmetic discrepancy already flagged, elevate risk
            if row.get("reconciliation_status", "").startswith("DISCREPANCY"):
                risk_level = "HIGH"
                flags.append("LEDGER_ARITHMETIC_MISMATCH")

            row["anomaly_flags"] = flags
            row["risk_level"] = risk_level
            row["tax_tag"] = tax_tag
            row["has_anomaly"] = len(flags) > 0
            analyzed.append(row)

        total_flagged = sum(1 for r in analyzed if r["has_anomaly"])
        high_risk_count = sum(1 for r in analyzed if r["risk_level"] == "HIGH")

        if high_risk_count > 0:
            overall_profile = "HIGH_RISK"
        elif total_flagged > 0:
            overall_profile = "MEDIUM_RISK"
        else:
            overall_profile = "CLEAN"

        summary = {
            "risk_profile": overall_profile,
            "total_flagged": total_flagged,
            "duplicates_count": duplicates_count // 2 if duplicates_count > 0 else 0,
            "outliers_count": outliers_count,
            "structuring_count": structuring_count,
            "tax_events_count": tax_events_count,
            "mean_debit": round(mean_debit, 2),
            "outlier_threshold": round(outlier_cutoff, 2) if outlier_cutoff != float("inf") else 0.0
        }

        return analyzed, summary
