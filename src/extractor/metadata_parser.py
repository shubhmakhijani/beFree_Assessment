import re
from typing import Dict, Any, Optional


class MetadataParser:
    """
    Extracts Account Holder Details & Statement Metadata using robust
    multi-bank regex anchor patterns and contextual heuristics.
    """

    KNOWN_BANKS = [
        "HDFC BANK", "STATE BANK OF INDIA", "SBI", "ICICI BANK", 
        "AXIS BANK", "KOTAK MAHINDRA BANK", "KOTAK BANK", 
        "BANK OF BARODA", "PUNJAB NATIONAL BANK", "PNB",
        "CANARA BANK", "UNION BANK OF INDIA", "INDUSIND BANK",
        "YES BANK", "FEDERAL BANK", "IDFC FIRST BANK",
        "CITIBANK", "STANDARD CHARTERED", "CHASE BANK", "HSBC"
    ]

    @classmethod
    def extract_metadata(cls, full_text: str) -> Dict[str, Any]:
        """
        Parses full document text to extract structured account metadata.
        """
        metadata = {
            "bank_name": cls._detect_bank(full_text),
            "account_holder": cls._extract_account_holder(full_text),
            "account_number": cls._extract_account_number(full_text),
            "ifsc_code": cls._extract_ifsc(full_text),
            "cif_number": cls._extract_cif(full_text),
            "account_type": cls._extract_account_type(full_text),
            "statement_period": cls._extract_statement_period(full_text),
            "opening_balance": cls._extract_balance(full_text, r"(?:Opening\s+Balance|B/F|Bal\s+b/f)"),
            "closing_balance": cls._extract_balance(full_text, r"(?:Closing\s+Balance|Total\s+Balance|C/F|Bal\s+c/f)")
        }
        return metadata

    @classmethod
    def _detect_bank(cls, text: str) -> str:
        text_upper = text.upper()
        
        ifsc_map = {
            "HDFC": "HDFC BANK",
            "SBIN": "STATE BANK OF INDIA",
            "ICIC": "ICICI BANK",
            "UTIB": "AXIS BANK",
            "KKBK": "KOTAK MAHINDRA BANK",
            "BARB": "BANK OF BARODA",
            "PUNB": "PUNJAB NATIONAL BANK",
            "CNRB": "CANARA BANK",
            "INDB": "INDUSIND BANK",
            "UBIN": "UNION BANK OF INDIA",
            "YESB": "YES BANK",
            "SCBL": "STANDARD CHARTERED BANK",
            "CITI": "CITIBANK",
            "HSBC": "HSBC BANK",
            "IDFB": "IDFC FIRST BANK",
            "FDRL": "FEDERAL BANK"
        }

        # Priority 1: Check IFSC explicitly linked to IFSC label in header lines
        ifsc_label_match = re.search(r"IFSC\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})\b", text_upper)
        if ifsc_label_match:
            prefix = ifsc_label_match.group(1)[:4]
            if prefix in ifsc_map:
                return ifsc_map[prefix]

        # Priority 2: Header IFSC search (top 30 lines) to avoid transaction narration remarks
        header_lines = text_upper.split("\n")[:30]
        header_txt = "\n".join(header_lines)
        header_ifsc = re.search(r"\b([A-Z]{4})0[A-Z0-9]{6}\b", header_txt)
        if header_ifsc:
            prefix = header_ifsc.group(1)
            if prefix in ifsc_map:
                return ifsc_map[prefix]

        # Priority 3: Check known banks in document header (first 30 lines)
        for bank in cls.KNOWN_BANKS:
            if re.search(r"\b" + re.escape(bank) + r"\b", header_txt) or bank.replace(" ", "") in header_txt:
                if bank in ["SBI", "SBIN"]:
                    return "STATE BANK OF INDIA"
                if bank in ["PNB", "PUNB"]:
                    return "PUNJAB NATIONAL BANK"
                if bank in ["STANDARD CHARTERED", "SCB"]:
                    return "STANDARD CHARTERED BANK"
                return bank

        # Priority 4: Full document IFSC code prefix (fallback)
        ifsc_match = re.search(r"\b([A-Z]{4})0[A-Z0-9]{6}\b", text_upper)
        if ifsc_match:
            prefix = ifsc_match.group(1)
            if prefix in ifsc_map:
                return ifsc_map[prefix]

        for bank in cls.KNOWN_BANKS:
            if re.search(r"\b" + re.escape(bank) + r"\b", text_upper) or bank.replace(" ", "") in text_upper:
                if bank in ["SBI", "SBIN"]:
                    return "STATE BANK OF INDIA"
                if bank in ["PNB", "PUNB"]:
                    return "PUNJAB NATIONAL BANK"
                if bank in ["STANDARD CHARTERED", "SCB"]:
                    return "STANDARD CHARTERED BANK"
                return bank

        # Generic heuristic if known bank not explicitly found (exclude NETBANK, etc.)
        match = re.search(r"([A-Z\s]+BANK(?:\s+OF\s+[A-Z]+)?)", text_upper)
        if match:
            candidate = match.group(1).strip()
            if candidate not in ["NETBANK", "INTERNET BANK"] and len(candidate) < 35:
                return candidate

        return "Bank Statement (General)"

    @classmethod
    def _extract_account_holder(cls, text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Helper to clean extraneous labels appearing on same line
        def clean_name(raw_name: str) -> str:
            cutoff_match = re.split(r"\b(?:IFSC|ACCOUNT|A/C|BRANCH|DATE|PERIOD|CIF|STATEMENT|PHONE|MOBILE)\b", raw_name, flags=re.IGNORECASE)
            cleaned = cutoff_match[0].strip(" :-")
            cleaned = re.sub(r"\s{2,}", " ", cleaned)
            return cleaned

        # Pattern 1: Explicit labels
        name_patterns = [
            r"(?:Customer|Account\s*Holder|Acc\s*Holder|Account)\s*Name\s*[:\-]?\s*([A-Za-z\s\.\&]+)",
            r"(?:Name)\s*[:\-]\s*([A-Za-z\s\.\&]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = clean_name(match.group(1).split("\n")[0])
                if 3 <= len(candidate) <= 45 and not any(kw in candidate.upper() for kw in ["STATEMENT", "BANK", "DATE", "NUMBER"]):
                    return candidate

        # Pattern 2: Honorific prefix search in top header lines (e.g. MR. ANUP DUBEY, MR SEENIVASAN)
        for line in lines[:30]:
            match = re.search(r"\b(MR|MRS|MS|DR|M/S)\.?\s+([A-Za-z\s\.]+)", line, re.IGNORECASE)
            if match:
                candidate = clean_name(match.group(1).upper() + " " + match.group(2).strip())
                if 3 <= len(candidate) <= 45 and not any(kw in candidate.upper() for kw in ["STATEMENT", "BANK", "DATE", "NUMBER", "ACCOUNT", "SAVINGS", "BRANCH"]):
                    return candidate

        # Pattern 3: Address block heuristic
        for i, line in enumerate(lines[:25]):
            if any(kw in line.upper() for kw in ["SAVINGS ACCOUNT", "CURRENT ACCOUNT", "ACCOUNT NO", "A/C NO"]):
                for offset in [-2, -1, 1, 2]:
                    idx = i + offset
                    if 0 <= idx < len(lines):
                        cand = clean_name(lines[idx])
                        if re.match(r"^[A-Z][a-zA-Z\s\.]{3,35}$", cand) and not any(x in cand.upper() for x in ["PAGE", "STATEMENT", "BRANCH", "BANK", "IFSC", "DATE", "COLONY", "APARTMENTS", "ROAD", "STREET", "NAGAR"]):
                            return cand

        return "Not Specified"

    @classmethod
    def _extract_account_number(cls, text: str) -> str:
        patterns = [
            r"(?:Account|A/c|Acct)\s*(?:No\.?|Number)?\s*[:\-]?\s*([0-9Xx\*\-]{9,22})",
            r"(?:Account\s*ID)\s*[:\-]?\s*([0-9Xx\*\-]{9,22})",
            r"\b([0-9]{11,18})\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                acc = match.group(1).strip()
                # Ensure it has at least some digits
                if sum(c.isdigit() for c in acc) >= 6:
                    return acc
        return "Not Specified"

    @classmethod
    def _extract_ifsc(cls, text: str) -> str:
        # Standard Indian IFSC Code: 4 uppercase letters, '0', 6 alphanumeric
        label_match = re.search(r"IFSC\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})\b", text, re.IGNORECASE)
        if label_match:
            return label_match.group(1).upper()

        header_lines = text.split("\n")[:30]
        header_txt = "\n".join(header_lines)
        match_hdr = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", header_txt)
        if match_hdr:
            return match_hdr.group(1).upper()

        match = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", text)
        if match:
            return match.group(1).upper()
        
        # Check for SWIFT / BIC or Routing Number
        swift_match = re.search(r"(?:SWIFT|BIC)\s*[:\-]?\s*([A-Z0-9]{8,11})", text, re.IGNORECASE)
        if swift_match:
            return swift_match.group(1).upper()

        routing_match = re.search(r"(?:Routing\s*No\.?|RTN)\s*[:\-]?\s*([0-9]{9})", text, re.IGNORECASE)
        if routing_match:
            return f"ROUTING-{routing_match.group(1)}"

        return "Not Specified"

    @classmethod
    def _extract_cif(cls, text: str) -> str:
        match = re.search(r"(?:CIF|Customer\s*ID|Cust\s*ID)\s*(?:No\.?|Number)?\s*[:\-]?\s*([0-9A-Za-z]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Not Specified"

    @classmethod
    def _extract_account_type(cls, text: str) -> str:
        text_upper = text.upper()
        if "SAVINGS" in text_upper or "SB ACCOUNT" in text_upper:
            return "Savings Account"
        if "CURRENT" in text_upper or "CA ACCOUNT" in text_upper:
            return "Current Account"
        if "OVERDRAFT" in text_upper or "OD ACCOUNT" in text_upper:
            return "Overdraft Account"
        if "SALARY" in text_upper:
            return "Salary Account"
        return "Standard Account"

    @classmethod
    def _extract_statement_period(cls, text: str) -> str:
        date_pattern = r"(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})"
        patterns = [
            rf"(?:Statement\s*Period|Period|Date\s*Range)\s*[:\-]?\s*({date_pattern})\s*(?:to|-|through)\s*({date_pattern})",
            rf"(?:From)\s*[:\-]?\s*({date_pattern})\s*(?:To)\s*[:\-]?\s*({date_pattern})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1).strip()} to {match.group(2).strip()}"
        return "Not Specified"

    @classmethod
    def _extract_balance(cls, text: str, anchor_regex: str) -> Optional[float]:
        pattern = rf"{anchor_regex}\s*[:\-]?\s*(?:INR|Rs\.?|₹|\$)?\s*([0-9,]+\.[0-9]{2}|[0-9,]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace(",", "").strip()
            try:
                return float(val_str)
            except ValueError:
                return None
        return None
