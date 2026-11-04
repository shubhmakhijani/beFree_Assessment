import re
from typing import Optional, Tuple, Dict, Any


class HeuristicRulesEngine:
    """
    Tier-1 Classification Engine: Rule-Based / Heuristic Pattern Matcher.
    Uses domain-specific financial regex patterns, merchant keywords, 
    and transaction direction (Debit vs Credit).
    """

    CATEGORIES = {
        "Salary & Income": [
            r"\bSALARY\b", r"\bPAYROLL\b", r"\bDIRECT DEP\b", r"\bSTIPEND\b",
            r"\bMONTHLY SAL\b", r"\bWAGES\b", r"\bBONUS\b", r"\bDIVIDEND\b",
            r"\bINTEREST PAID\b", r"\bINT\.?PD\b", r"\bINTEREST CREDIT\b",
            r"\bINCENTIVE\b", r"\bREFUND\b"
        ],
        "Food & Dining": [
            r"\bSWIGGY\b", r"\bZOMATO\b", r"\bDOMINOS\b", r"\bPIZZA\b", 
            r"\bMCDONALDS?\b", r"\bKFC\b", r"\bBURGER KING\b", r"\bSTARBUCKS\b",
            r"\bCAFE\b", r"\bRESTAURANT\b", r"\bBARBEQUE\b", r"\bBAKERY\b",
            r"\bCHAAYOS\b", r"\bCHAI POINT\b", r"\bSUBWAY\b", r"\bEATS\b",
            r"\bFOOD\b", r"\bDINE\b", r"\bDHABA\b", r"\bBREWERY\b"
        ],
        "Groceries & Supermarket": [
            r"\bBLINKIT\b", r"\bZEPTO\b", r"\bBIGBASKET\b", r"\bDMART\b", 
            r"\bRELIANCE FRESH\b", r"\bSPENCERS\b", r"\bMORE RETAIL\b", 
            r"\bGROCERY\b", r"\bSUPERMARKET\b", r"\bKIRANA\b", r"\bPROVISION\b",
            r"\bNATURES BASKET\b", r"\bVEGETABLES\b", r"\bFRUITS\b", r"\bMILK\b",
            r"\bCOUNTRY DELIGHT\b", r"\bBB DAILY\b"
        ],
        "Shopping & E-Commerce": [
            r"\bAMAZON\b", r"\bFLIPKART\b", r"\bMYNTRA\b", r"\bMEESHO\b",
            r"\bAJIO\b", r"\bNYKAA\b", r"\bTATA CLIQ\b", r"\bSHOPPING\b",
            r"\bZARA\b", r"\bH&M\b", r"\bUNIQLO\b", r"\bDECATHLON\b",
            r"\bLIFESTYLE\b", r"\bSHOPPERS STOP\b", r"\bRETAIL\b", r"\bSTORE\b"
        ],
        "Utilities & Bills": [
            r"\bELECTRICITY\b", r"\bPOWER\b", r"\bBESCOM\b", r"\bTNEB\b", 
            r"\bUPPCL\b", r"\bWATER\b", r"\bGAS\b", r"\bCYLINDER\b", 
            r"\bINDANE\b", r"\bHP GAS\b", r"\bBHARAT GAS\b", r"\bAIRTEL\b",
            r"\bJIO\b", r"\bVI\b", r"\bVODAFONE\b", r"\bBSNL\b",
            r"\bBROADBAND\b", r"\bFIBERNET\b", r"\bACT\b", r"\bWI-FI\b",
            r"\bDTH\b", r"\bTATA PLAY\b", r"\bMAINTENANCE\b", r"\bBILLPAY\b"
        ],
        "Travel & Commute": [
            r"\bUBER\b", r"\bOLA\b", r"\bRAPIDO\b", r"\bIRCTC\b", 
            r"\bRAILWAY\b", r"\bRED BUS\b", r"\bREDBUS\b", r"\bMAKEMYTRIP\b",
            r"\bGOIBIBO\b", r"\bEASEMYTRIP\b", r"\bINDIGO\b", r"\bAIR INDIA\b",
            r"\bSPICEJET\b", r"\bPETROL\b", r"\bDIESEL\b", r"\bHPCL\b",
            r"\bBPCL\b", r"\bIOCL\b", r"\bSHELL\b", r"\bFUEL\b",
            r"\bFASTAG\b", r"\bTOLL\b", r"\bMETRO\b", r"\bFLIGHT\b"
        ],
        "Investments & Wealth": [
            r"\bZERODHA\b", r"\bGROWW\b", r"\bUPSTOX\b", r"\bANGEL ONE\b",
            r"\bMUTUAL FUND\b", r"\bMF\b", r"\bSIP\b", r"\bCAMSONLINE\b",
            r"\bKFINTECH\b", r"\bSECURITIES\b", r"\bNPS\b", r"\bPPF\b",
            r"\bGOLD\b", r"\bSTOCK\b", r"\bBROKING\b", r"\bINDMONEY\b"
        ],
        "Loans & EMI": [
            r"\bEMI\b", r"\bLOAN\b", r"\bBAJAJ FIN\b", r"\bBAJAJ FINANCE\b",
            r"\bHOME LOAN\b", r"\bAUTO LOAN\b", r"\bCAR LOAN\b", r"\bPERSONAL LOAN\b",
            r"\bCREDIT CARD\b", r"\bCC PAYMENT\b", r"\bCRED\b", r"\bHDFC LOAN\b",
            r"\bSBI LOAN\b", r"\bICICI LOAN\b", r"\bFINANCE\b"
        ],
        "Bank Charges & Taxes": [
            r"\bANNUAL CHARGE\b", r"\bSMS CHG\b", r"\bMIN BAL\b", r"\bMINIMUM BALANCE\b",
            r"\bGST\b", r"\bSERVICE TAX\b", r"\bCHQ RETURN\b", r"\bPENALTY\b",
            r"\bDEBIT CARD FEE\b", r"\bATM CHARGE\b", r"\bCHG\b", r"\bFEE\b",
            r"\bINTEREST DEBIT\b"
        ],
        "Entertainment & Subscriptions": [
            r"\bNETFLIX\b", r"\bSPOTIFY\b", r"\bAMAZON PRIME\b", r"\bHOTSTAR\b",
            r"\bDISNEY\b", r"\bYOUTUBE\b", r"\bBOOKMYSHOW\b", r"\bPVR\b",
            r"\bINOX\b", r"\bCINEMA\b", r"\bAPPLE\.COM/BILL\b", r"\bGOOGLE PLAY\b"
        ],
        "Healthcare & Medical": [
            r"\bAPOLLO\b", r"\bPHARMACY\b", r"\bMEDPLUS\b", r"\b1MG\b",
            r"\bNETMEDS\b", r"\bHOSPITAL\b", r"\bCLINIC\b", r"\bDOCTOR\b",
            r"\bLAB\b", r"\bDIAGNOSTIC\b", r"\bHEALTHCARE\b", r"\bMEDICINE\b",
            r"\bPATHOLOGY\b", r"\bMAX HEALTH\b", r"\bFORTIS\b"
        ],
        "Education & Fees": [
            r"\bSCHOOL\b", r"\bCOLLEGE\b", r"\bUNIVERSITY\b", r"\bTUITION\b",
            r"\bFEES\b", r"\bUDEMY\b", r"\bCOURSERA\b", r"\bEDX\b",
            r"\bACADEMY\b", r"\bINSTITUTE\b", r"\bCOACHING\b"
        ],
        "Transfers & Personal": [
            r"\bUPI\b", r"\bIMPS\b", r"\bNEFT\b", r"\bRTGS\b", 
            r"\bTRANSFER TO\b", r"\bTRANSFER FROM\b", r"\bSENT TO\b",
            r"\bRECEIVED FROM\b", r"\bSELF\b", r"\bFUNDS TFR\b"
        ]
    }

    @classmethod
    def classify(cls, description: str, debit: float = 0.0, credit: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Applies directional logic and regex matching.
        
        Returns:
            dict with category, confidence=1.0, and matched rule, or None if no rule matches.
        """
        desc_upper = description.upper()

        # Directional Rule 1: Credits from employer or containing salary keywords
        if credit > 0:
            for pat in cls.CATEGORIES["Salary & Income"]:
                if re.search(pat, desc_upper):
                    return {
                        "category": "Salary & Income",
                        "confidence": 1.0,
                        "method": "HEURISTIC_RULE",
                        "rule_matched": pat
                    }

        # Check all specific categories first (excluding generic transfers)
        priority_categories = [
            "Food & Dining",
            "Groceries & Supermarket",
            "Utilities & Bills",
            "Travel & Commute",
            "Shopping & E-Commerce",
            "Investments & Wealth",
            "Loans & EMI",
            "Entertainment & Subscriptions",
            "Healthcare & Medical",
            "Education & Fees",
            "Bank Charges & Taxes"
        ]

        for cat in priority_categories:
            patterns = cls.CATEGORIES[cat]
            for pat in patterns:
                if re.search(pat, desc_upper):
                    return {
                        "category": cat,
                        "confidence": 1.0,
                        "method": "HEURISTIC_RULE",
                        "rule_matched": pat
                    }

        # Fallback to Transfers & Personal if generic transfer keywords appear
        for pat in cls.CATEGORIES["Transfers & Personal"]:
            if re.search(pat, desc_upper):
                return {
                    "category": "Transfers & Personal",
                    "confidence": 0.95,
                    "method": "HEURISTIC_RULE",
                    "rule_matched": pat
                }

        return None
