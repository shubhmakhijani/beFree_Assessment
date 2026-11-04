from typing import Dict, Any, List
from src.classifier.rules_engine import HeuristicRulesEngine
from src.classifier.ml_engine import MLEngine


class HybridTransactionClassifier:
    """
    Hybrid Classification Arbitrator combining:
    1. Heuristic Rule-Based Engine (High Precision)
    2. Traditional Machine Learning Model (High Recall & Generalization)
    
    Adheres strictly to the Non-LLM requirement.
    """

    CONFIDENCE_THRESHOLD = 0.35

    @classmethod
    def classify_transaction(
        cls, 
        description: str, 
        debit: float = 0.0, 
        credit: float = 0.0
    ) -> Dict[str, Any]:
        """
        Classifies a single transaction using the two-tier hybrid architecture.
        """
        # Step 1: Query Tier-1 Heuristic Rules Engine
        rule_result = HeuristicRulesEngine.classify(description, debit=debit, credit=credit)
        if rule_result:
            return {
                "category": rule_result["category"],
                "confidence": rule_result["confidence"],
                "classification_engine": "HEURISTIC_RULE",
                "details": f"Matched pattern: {rule_result.get('rule_matched', 'Direct Rule')}"
            }

        # Step 2: Query Tier-2 Traditional ML Engine
        ml_result = MLEngine.predict(description)
        
        if ml_result["confidence"] >= cls.CONFIDENCE_THRESHOLD:
            return {
                "category": ml_result["category"],
                "confidence": ml_result["confidence"],
                "classification_engine": "TRADITIONAL_ML",
                "details": f"TF-IDF + LogisticRegression (Prob: {ml_result['confidence'] * 100:.1f}%)"
            }
        else:
            # Below confidence threshold: Flag for accountant review
            top_rec = ml_result["top_suggestions"][0]["category"] if ml_result["top_suggestions"] else "General"
            return {
                "category": "Uncategorized / Needs Review",
                "confidence": ml_result["confidence"],
                "classification_engine": "UNCERTAIN_LOW_CONFIDENCE",
                "details": f"Recommended candidate: {top_rec} (Prob: {ml_result['confidence'] * 100:.1f}%)"
            }

    @classmethod
    def classify_all(cls, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches a list of transaction dictionaries with assigned categories and confidence scores.
        """
        enriched = []
        for txn in transactions:
            desc = txn.get("description", "")
            debit = float(txn.get("debit", 0.0) or 0.0)
            credit = float(txn.get("credit", 0.0) or 0.0)

            cls_res = cls.classify_transaction(desc, debit=debit, credit=credit)
            
            merged = dict(txn)
            merged["category"] = cls_res["category"]
            merged["confidence"] = cls_res["confidence"]
            merged["classification_engine"] = cls_res["classification_engine"]
            merged["classification_details"] = cls_res["details"]
            enriched.append(merged)

        return enriched
