
import joblib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"

class CustomerAI:
    def __init__(self):
        self.domain = joblib.load(MODEL_DIR / "domain_voting_model.joblib")
        self.engagement = joblib.load(MODEL_DIR / "engagement_voting_model.joblib")
        self.purchase = joblib.load(MODEL_DIR / "purchase_intent_voting_model.joblib")
        self.complexity = joblib.load(MODEL_DIR / "complexity_voting_model.joblib")
        self.intent = joblib.load(MODEL_DIR / "intent_model.joblib")
        self.features = joblib.load(MODEL_DIR / "features.joblib")

    def _row(self, data):
        row = {}
        for k in self.features:
            if k in data:
                row[k] = data[k]
            elif k == "marital_status":
                row[k] = "single"
            elif k == "credit_score":
                row[k] = 650
            elif k in ["existing_policy", "selected_category"]:
                row[k] = "none"
            else:
                row[k] = 0
        return pd.DataFrame([row])

    @staticmethod
    def _prediction(model, X):
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        classes = model.classes_
        scores = {
            str(cls): round(float(prob), 4)
            for cls, prob in zip(classes, probabilities)
        }
        confidence = float(max(probabilities))
        return str(prediction).lower(), confidence, scores

    def analyze(self, data, message=""):
        X = self._row(data)

        inferred_domain, inferred_domain_conf, domain_scores = self._prediction(self.domain, X)
        engagement, engagement_conf, engagement_scores = self._prediction(self.engagement, X)
        purchase, purchase_conf, purchase_scores = self._prediction(self.purchase, X)
        complexity, complexity_conf, complexity_scores = self._prediction(self.complexity, X)
        comparison_fields = [
            "health_comparisons", "life_comparisons",
            "vehicle_comparisons", "general_comparisons"
        ]
        comparison_count = sum(
            max(float(data.get(field, 0) or 0), 0) for field in comparison_fields
        )
        credit_score = int(data.get("credit_score", 650) or 650)
        existing_policy = str(data.get("existing_policy", "none")).lower()
        senior_request = any(
            phrase in message.lower()
            for phrase in ["senior agent", "expert agent", "supervisor", "manager"]
        ) if message else False

        intent = None
        intent_conf = None
        intent_scores = None

        if message and message.strip():
            intent = str(self.intent.predict([message])[0])
            probs = self.intent.predict_proba([message])[0]
            classes = self.intent.classes_
            intent_scores = {
                str(cls): round(float(prob), 4)
                for cls, prob in zip(classes, probs)
            }
            intent_conf = float(max(probs))

        # Explicit category takes priority over inferred behavior.
        selected = str(data.get("selected_category", "none")).lower()
        if selected in {"health", "life", "vehicle", "general"}:
            domain = selected
            domain_source = "explicit_selection"
            domain_conf = 1.0
        else:
            domain = inferred_domain
            domain_source = "four_model_voting"
            domain_conf = inferred_domain_conf

        return {
            "domain": domain,
            "domain_source": domain_source,
            "domain_confidence": round(domain_conf, 4),
            "inferred_domain": inferred_domain,
            "inferred_domain_confidence": round(inferred_domain_conf, 4),
            "domain_scores": domain_scores,

            "intent": intent,
            "intent_confidence": round(intent_conf, 4) if intent_conf is not None else None,
            "intent_scores": intent_scores,

            "engagement": engagement,
            "engagement_confidence": round(engagement_conf, 4),
            "engagement_scores": engagement_scores,

            "purchase_intent": purchase,
            "purchase_confidence": round(purchase_conf, 4),
            "purchase_scores": purchase_scores,

            "complexity": complexity,
            "complexity_confidence": round(complexity_conf, 4),
            "complexity_scores": complexity_scores,
            "comparison_count": int(comparison_count),
            "credit_score": max(300, min(850, credit_score)),
            "existing_policy": existing_policy,
            "senior_request": senior_request
        }
