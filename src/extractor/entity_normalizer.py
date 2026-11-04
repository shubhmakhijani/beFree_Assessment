import re
from typing import Dict, Any, List


class EntityNormalizer:
    """
    Bank Description Normalizer:
    Decomposes raw, unstructured bank statement narrations into 
    standardized enterprise accounting fields:
      - Clean Counterparty / Vendor Name
      - Payment Channel (UPI, NEFT, RTGS, IMPS, POS, ATM, ACH, Cheque)
      - Transaction Reference / UTR Number
    """

    KNOWN_ENTITIES = [
        # Food & Groceries
        ("SWIGGY", "Swiggy"),
        ("ZOMATO", "Zomato"),
        ("BLINKIT", "Blinkit"),
        ("ZEPTO", "Zepto"),
        ("BIGBASKET", "BigBasket"),
        ("INSTAMART", "Swiggy Instamart"),
        ("STARBUCKS", "Starbucks"),
        ("MCDONALDS", "McDonald's"),
        ("DOMINOS", "Domino's Pizza"),
        
        # E-Commerce & Retail
        ("AMAZON", "Amazon"),
        ("FLIPKART", "Flipkart"),
        ("MYNTRA", "Myntra"),
        ("MEESHO", "Meesho"),
        ("NYKAA", "Nykaa"),
        ("DMART", "D-Mart"),
        ("RELIANCE", "Reliance Retail"),
        ("TATA 1MG", "Tata 1mg"),
        ("APOLLO", "Apollo Pharmacy"),
        
        # Ride Hailing & Travel
        ("UBER", "Uber"),
        ("OLA", "Ola Cabs"),
        ("RAPIDO", "Rapido"),
        ("IRCTC", "IRCTC"),
        ("MAKEMYTRIP", "MakeMyTrip"),
        ("INDIGO", "IndiGo Airlines"),
        ("AIR INDIA", "Air India"),
        
        # Telecom & Utilities
        ("AIRTEL", "Airtel"),
        ("JIO", "Reliance Jio"),
        ("VODAFONE", "Vodafone Idea"),
        ("VI ", "Vodafone Idea"),
        ("BESCOM", "BESCOM Electricity"),
        ("TNEB", "TNEB Power"),
        ("ADANI", "Adani Electricity"),
        ("IGL", "Indraprastha Gas"),
        
        # Subscriptions & Entertainment
        ("NETFLIX", "Netflix"),
        ("SPOTIFY", "Spotify"),
        ("HOTSTAR", "Disney+ Hotstar"),
        ("PRIME VIDEO", "Amazon Prime"),
        ("YOUTUBE", "YouTube Premium"),
        ("BOOKMYSHOW", "BookMyShow"),
        ("PVR", "PVR Cinemas"),
        
        # Financial & Wealth
        ("ZERODHA", "Zerodha"),
        ("GROWW", "Groww"),
        ("KIMS", "CAMS Mutual Fund"),
        ("KFINTECH", "KFintech"),
        ("HDFC LIFE", "HDFC Life Insurance"),
        ("LIC", "Life Insurance Corp (LIC)"),
        ("ICICI PRU", "ICICI Prudential"),
        ("BAJAJ FIN", "Bajaj Finance"),
        ("CRED", "CRED Payments"),
        
        # Tech & Corporates
        ("GOOGLE", "Google Workspace"),
        ("MICROSOFT", "Microsoft 365"),
        ("AWS", "Amazon Web Services"),
        ("INFOSYS", "Infosys Ltd"),
        ("TCS", "Tata Consultancy Services"),
        ("WIPRO", "Wipro Ltd")
    ]

    CHANNEL_PATTERNS = [
        (re.compile(r"\bUPI[/-]|\bVPA\b|\bGPAY\b|\bPHONEPE\b|\bPAYTM\b", re.IGNORECASE), "UPI"),
        (re.compile(r"\bNEFT\b", re.IGNORECASE), "NEFT"),
        (re.compile(r"\bRTGS\b", re.IGNORECASE), "RTGS"),
        (re.compile(r"\bIMPS\b", re.IGNORECASE), "IMPS"),
        (re.compile(r"\bPOS\b|\bCARD\b|\bDEBIT\s*CARD\b|\bVISA\b|\bMASTERCARD\b", re.IGNORECASE), "POS_CARD"),
        (re.compile(r"\bATM\b|\bCASH\s*WDL\b|\bCASH\s*DEP\b", re.IGNORECASE), "ATM_CASH"),
        (re.compile(r"\bACH\b|\bNACH\b|\bECS\b|\bMANDATE\b", re.IGNORECASE), "ACH_NACH"),
        (re.compile(r"\bCHQ\b|\bCHEQUE\b|\bCLEARING\b", re.IGNORECASE), "CHEQUE"),
        (re.compile(r"\bNETBANKING\b|\bINET\b|\bFT\b|\bINTERNAL\s*TRANSFER\b", re.IGNORECASE), "NET_BANKING"),
        (re.compile(r"\bCHG\b|\bFEE\b|\bSMS\s*CHG\b|\bANNUAL\s*MAINT\b|\bINT\.PD\b", re.IGNORECASE), "BANK_CHARGES")
    ]

    UTR_REGEX = re.compile(r"\b([A-Z0-9]{10,22})\b")

    @classmethod
    def normalize(cls, description: str) -> Dict[str, Any]:
        """
        Deconstructs a single narration into clean metadata.
        """
        desc_upper = description.upper()

        # 1. Detect Channel
        channel = "OTHER"
        for pat, chan_name in cls.CHANNEL_PATTERNS:
            if pat.search(desc_upper):
                channel = chan_name
                break

        # 2. Extract Clean Counterparty / Entity
        counterparty = None
        for keyword, clean_name in cls.KNOWN_ENTITIES:
            if keyword in desc_upper:
                counterparty = clean_name
                break

        if not counterparty:
            # Fallback heuristic: Extract primary alphanumeric token
            parts = [p.strip() for p in re.split(r"[/_-]", description) if len(p.strip()) >= 3]
            # Ignore channel tokens
            filtered_parts = [p for p in parts if not re.match(r"^(UPI|NEFT|RTGS|IMPS|POS|ACH|CMS|VPA)$", p, re.IGNORECASE)]
            counterparty = filtered_parts[0] if filtered_parts else description[:25].strip()

        # 3. Extract Reference / UTR
        tokens = description.split()
        ref_no = None
        for tok in tokens:
            clean_tok = re.sub(r"[^A-Za-z0-9]", "", tok)
            if 10 <= len(clean_tok) <= 22 and any(c.isdigit() for c in clean_tok):
                ref_no = clean_tok
                break

        return {
            "clean_counterparty": counterparty,
            "payment_channel": channel,
            "reference_number": ref_no or "N/A"
        }

    @classmethod
    def normalize_transactions(cls, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches a list of transaction dictionaries with normalized accounting entities.
        """
        normalized_list = []
        for txn in transactions:
            row = dict(txn)
            norm = cls.normalize(row.get("description", ""))
            row.update(norm)
            normalized_list.append(row)
        return normalized_list
