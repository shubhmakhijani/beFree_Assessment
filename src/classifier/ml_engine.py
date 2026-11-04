import os
import joblib
import numpy as np
from typing import Dict, Any, List
from src.classifier.train_model import clean_banking_narration


class MLEngine:
    """
    Tier-2 Classification Engine: Traditional Machine Learning.
    Uses TF-IDF feature extraction + Calibrated Logistic Regression.
    """

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "transaction_classifier.joblib")

    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            if not os.path.exists(cls.MODEL_PATH):
                from src.classifier.train_model import train_and_save_model
                train_and_save_model(cls.MODEL_PATH)
            cls._pipeline = joblib.load(cls.MODEL_PATH)
        return cls._pipeline

    @classmethod
    def predict(cls, description: str, top_k: int = 2) -> Dict[str, Any]:
        """
        Classifies a single transaction description.
        
        Returns:
            dict containing:
                - category: str (predicted class)
                - confidence: float (0.0 to 1.0)
                - method: 'TRADITIONAL_ML'
                - top_suggestions: list of (class, prob)
        """
        pipeline = cls.get_pipeline()
        cleaned_text = clean_banking_narration(description)
        
        if not cleaned_text:
            return {
                "category": "Uncategorized / Needs Review",
                "confidence": 0.0,
                "method": "TRADITIONAL_ML",
                "top_suggestions": []
            }

        probabilities = pipeline.predict_proba([cleaned_text])[0]
        classes = pipeline.classes_

        top_indices = np.argsort(probabilities)[::-1][:top_k]
        top_category = classes[top_indices[0]]
        top_confidence = float(probabilities[top_indices[0]])

        suggestions = [
            {"category": classes[idx], "confidence": round(float(probabilities[idx]), 3)}
            for idx in top_indices
        ]

        return {
            "category": top_category,
            "confidence": round(top_confidence, 3),
            "method": "TRADITIONAL_ML",
            "top_suggestions": suggestions
        }

    @classmethod
    def predict_batch(cls, descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        Batch prediction for high performance.
        """
        return [cls.predict(d) for d in descriptions]
