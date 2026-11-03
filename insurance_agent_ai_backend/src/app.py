
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import pandas as pd
import traceback

from predictor import CustomerAI
from router import AgentRouter

app = Flask(__name__)
CORS(app)

ROOT = Path(__file__).resolve().parents[1]
customers_file = ROOT / "data" / "customers_runtime_clean.csv"

ai = None
router = None

def init_services():
    global ai, router
    if ai is None:
        ai = CustomerAI()
    if router is None:
        router = AgentRouter()

def save_customer(customer, analysis, assignment):
    record = {key: customer.get(key) for key in ai.features}
    record.update({
        "credit_score": analysis["credit_score"],
        "comparison_count": analysis["comparison_count"],
        "predicted_domain": analysis["domain"],
        "intent": analysis["intent"],
        "engagement": analysis["engagement"],
        "purchase_intent": analysis["purchase_intent"],
        "complexity": analysis["complexity"],
        "assigned_agent_id": assignment["agent"]["agent_id"] if assignment["assigned"] else None
    })
    row = pd.DataFrame([record])
    if customers_file.exists():
        row.to_csv(customers_file, mode="a", header=False, index=False)
    else:
        row.to_csv(customers_file, index=False)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "insurance-agent-ai"})

MODEL_INFO = {
    "algorithms": ["Logistic Regression", "Decision Tree", "Random Forest", "K-Nearest Neighbors"],
    "voting": "soft_voting",
    "training_data": "synthetic_development_data",
    "production_validated": False,
    "warning": "Predictions require validation against authorized real customer data before production use."
}

@app.post("/analyze")
def analyze():
    try:
        init_services()
        payload = request.get_json(force=True)
        customer = payload.get("customer", payload)
        message = payload.get("message", "")
        language = payload.get("language", "English")

        analysis = ai.analyze(customer, message)
        assignment = router.assign(analysis, language)
        save_customer(customer, analysis, assignment)

        return jsonify({
            "success": True,
            "model_info": MODEL_INFO,
            "analysis": analysis,
            "assignment": assignment
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.post("/assign")
def assign():
    try:
        init_services()
        payload = request.get_json(force=True)
        customer = payload.get("customer", payload)
        message = payload.get("message", "")
        language = payload.get("language", "English")

        analysis = ai.analyze(customer, message)
        assignment = router.assign(analysis, language)

        return jsonify({
            "success": True,
            "model_info": MODEL_INFO,
            "analysis": analysis,
            "assignment": assignment
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.get("/agents")
def agents():
    init_services()
    result = router.agents.drop(columns=["domains_set", "languages_set"]).to_dict(orient="records")
    return jsonify(result)

if __name__ == "__main__":
    print("Starting Insurance Agent AI backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)
