import re
from datetime import datetime
from typing import List, Dict, Any, Optional


class RowStitcher:
    """
    Handles multi-line narration merging, noise filtering,
    date normalization, and numeric amount cleaning.
    """

    DATE_PATTERNS = [
        (r"^\d{2}/\d{2}/\d{4}$", "%d/%m/%Y"),
        (r"^\d{2}-\d{2}-\d{4}$", "%d-%m-%Y"),
        (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
        (r"^\d{2}/\d{2}/\d{2}$", "%d/%m/%y"),
        (r"^\d{2}-\d{2}-\d{2}$", "%d-%m-%y"),
        (r"^\d{2}\s+[A-Za-z]{3}\s+\d{4}$", "%d %b %Y"),
        (r"^\d{2}-[A-Za-z]{3}-\d{4}$", "%d-%b-%Y"),
        (r"^\d{2}-[A-Za-z]{3}-\d{2}$", "%d-%b-%y"),
        (r"^\d{2}\s+[A-Za-z]{3}\s+\d{2}$", "%d %b %y"),
        (r"^\d{1,2}/\d{1,2}/\d{4}$", "%d/%m/%Y"),
    ]

    HEADER_KEYWORDS = [
        "DATE", "NARRATION", "DESCRIPTION", "PARTICULARS", 
        "DEBIT", "CREDIT", "WITHDRAWAL", "DEPOSIT", "BALANCE", 
        "CHQ", "CHEQUE", "REF", "VALUE DATE"
    ]

    NOISE_ROW_PATTERNS = [
        r"^PAGE\s+\d+",
        r"^STATEMENT\s+SUMMARY",
        r"^TOTAL\s*[:\-]?",
        r"^OPENING\s+BALANCE",
        r"^CLOSING\s+BALANCE",
        r"^CARRIED\s+FORWARD",
        r"^BROUGHT\s+FORWARD",
        r"^\*+\s*END\s+OF\s+STATEMENT\s*\*+"
    ]

    @classmethod
    def clean_amount(cls, val: Any) -> float:
        """
        Converts text amount representation into float.
        Handles currencies, commas, trailing Dr/Cr, and parentheses.
        """
        if val is None:
            return 0.0
        val_str = str(val).strip()
        if not val_str or val_str in ["-", "--", "NA", "N/A", "nil", "NIL", "0"]:
            return 0.0

        # Remove currency symbols and formatting characters
        val_str = re.sub(r"[₹\$£€INRRs\.,\s]", lambda m: "." if m.group(0) == "." else "", val_str)
        # Fix multiple dots if commas were cleaned wrong
        if val_str.count(".") > 1:
            parts = val_str.split(".")
            val_str = "".join(parts[:-1]) + "." + parts[-1]

        # Handle parentheses representing negative numbers (e.g. (500.00))
        is_negative = False
        if val_str.startswith("(") and val_str.endswith(")"):
            is_negative = True
            val_str = val_str[1:-1]
        elif val_str.endswith("-"):
            is_negative = True
            val_str = val_str[:-1]

        # Handle trailing Cr or Dr
        val_upper = val_str.upper()
        if val_upper.endswith("DR"):
            val_str = val_upper.replace("DR", "").strip()
        elif val_upper.endswith("CR"):
            val_str = val_upper.replace("CR", "").strip()

        try:
            amount = float(val_str)
            return -amount if is_negative else amount
        except ValueError:
            return 0.0

    @classmethod
    def normalize_date(cls, val: Any) -> Optional[str]:
        """
        Detects and parses diverse date formats into standard ISO 'YYYY-MM-DD'.
        """
        if not val:
            return None
        text = str(val).strip()
        # Extract potential date substring
        date_cand_match = re.search(r"(\d{1,4}[\/\-\.\s][A-Za-z0-9]{1,3}[\/\-\.\s]\d{2,4})", text)
        cand = date_cand_match.group(1).strip() if date_cand_match else text

        for pattern, dt_format in cls.DATE_PATTERNS:
            if re.match(pattern, cand, re.IGNORECASE):
                try:
                    dt = datetime.strptime(cand, dt_format)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        # Try flexible dateutil parser if available
        try:
            from dateutil import parser as dt_parser
            dt = dt_parser.parse(cand, dayfirst=True)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    @classmethod
    def is_header_row(cls, row_cells: List[str]) -> bool:
        """
        Determines if a row is a table header row (e.g. Date, Narration, Debit...).
        """
        joined = " ".join(str(c).upper() for c in row_cells if c)
        match_count = sum(1 for kw in cls.HEADER_KEYWORDS if kw in joined)
        return match_count >= 3

    @classmethod
    def is_noise_row(cls, row_cells: List[str]) -> bool:
        """
        Checks if a row is a summary, disclaimer, or pagination artifact.
        """
        joined = " ".join(str(c).strip() for c in row_cells if c).upper()
        if not joined:
            return True
        for pattern in cls.NOISE_ROW_PATTERNS:
            if re.search(pattern, joined):
                return True
        return False

    @classmethod
    def stitch_raw_rows(cls, raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw extracted table rows, filters noise/headers, and stitches
        multi-line narration strings to the preceding parent transaction.
        
        Expected raw row keys: 'date', 'description', 'debit', 'credit', 'balance'
        """
        stitched = []
        last_txn = None

        for row in raw_rows:
            raw_date = row.get("date", "")
            raw_desc = str(row.get("description", "")).strip()
            debit_val = cls.clean_amount(row.get("debit"))
            credit_val = cls.clean_amount(row.get("credit"))
            balance_val = cls.clean_amount(row.get("balance"))

            norm_date = cls.normalize_date(raw_date)

            # Case 1: Check if this is a header row
            if cls.is_header_row([str(v) for v in row.values()]):
                continue

            # Case 2: Check if this is a noise/summary row
            if cls.is_noise_row([str(v) for v in row.values()]):
                continue

            # Case 3: Complete Transaction row
            # It has a valid date and at least one financial amount or balance
            if norm_date and (debit_val > 0 or credit_val > 0 or balance_val != 0 or row.get("balance") is not None):
                last_txn = {
                    "date": norm_date,
                    "description": raw_desc,
                    "debit": debit_val,
                    "credit": credit_val,
                    "balance": balance_val,
                    "raw_parts": [raw_desc]
                }
                stitched.append(last_txn)

            # Case 4: Multi-line Continuation row
            # Lacks date and debit/credit amounts, but contains description text
            elif last_txn is not None and raw_desc and not norm_date and debit_val == 0 and credit_val == 0:
                # Append narration line
                last_txn["description"] += " " + raw_desc
                last_txn["raw_parts"].append(raw_desc)
                # If balance was empty on parent row but appears here, populate it
                if last_txn["balance"] == 0 and balance_val != 0:
                    last_txn["balance"] = balance_val

            # Case 5: Transaction without valid date format, but with clear debit/credit & balance
            elif last_txn is not None and not norm_date and (debit_val > 0 or credit_val > 0) and balance_val != 0:
                # Fallback to previous transaction date if same batch
                last_txn = {
                    "date": last_txn["date"],
                    "description": raw_desc,
                    "debit": debit_val,
                    "credit": credit_val,
                    "balance": balance_val,
                    "raw_parts": [raw_desc]
                }
                stitched.append(last_txn)

        # Final cleanup on stitched narrations
        for txn in stitched:
            txn["description"] = re.sub(r"\s{2,}", " ", txn["description"]).strip()
            if "raw_parts" in txn:
                del txn["raw_parts"]

        return stitched
