"""
PolicyBuzar - Flask Application Backend
Serves the dynamic AI routing platform with endpoints:
- POST /api/predict: Full 5-stage classification & intelligent agent allocation
- POST /api/train: Retrain ML models on synthetic dataset
- GET /api/model-metrics: Returns evaluation metrics for LR, DT, RF, KNN, Ensemble
- GET /api/dataset/summary: Returns synthetic dataset statistics
- GET /api/agents: Returns all synthetic agents and live availability
- GET /api/health: Health check and engine status
- POST /api/feedback: Stores customer and agent feedback outcomes
- GET /api/scenarios: Returns 10 demonstration scenarios
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.services.routing_engine import routing_engine
from backend.services.sensitivity_tracker import analyze_change
from backend.database.db_service import db_service
from backend.config.scenarios import SCENARIOS
from backend.config.policy_config import DEFAULT_CUSTOMER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
METRICS_PATH = os.path.join(BASE_DIR, "models", "saved", "model_metrics.json")
SUMMARY_PATH = os.path.join(BASE_DIR, "data", "dataset_summary.json")

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app)


# -------------------------------------------------------------
# SERVE FRONTEND (Single-Process Full-Stack Support)
# -------------------------------------------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return app.send_static_file(path)
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return app.send_static_file("index.html")
    return jsonify({
        "status": "running",
        "message": "PolicyBuzar Flask Backend API is active. Frontend is available at port 3000 in dev mode or in frontend/dist."
    }), 200


# -------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    db_stats = db_service.get_stats()
    models_ready = (
        routing_engine.domain_bundle is not None and
        routing_engine.engagement_bundle is not None and
        routing_engine.willingness_bundle is not None and
        routing_engine.complexity_bundle is not None and
        routing_engine.intent_bundle is not None
    )
    return jsonify({
        "status": "healthy" if models_ready else "degraded",
        "models_loaded": models_ready,
        "database": db_stats,
        "engine": "salesInternAi Dynamic Multi-Model AI Routing Engine v2.0"
    }), 200


# -------------------------------------------------------------
# PREDICT
# -------------------------------------------------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        body = request.get_json(force=True) or {}
        customer_data = body.get("customer", body)
        prev_input = body.get("previous_customer")
        prev_result = body.get("previous_prediction")

        # Merge with default fields to ensure zero missing input errors
        merged_customer = dict(DEFAULT_CUSTOMER)
        merged_customer.update(customer_data)

        # Run 5-stage AI classification pipeline
        result = routing_engine.process_customer(merged_customer)

        # Compute real-time sensitivity analysis if previous state provided
        sensitivity = None
        if prev_input:
            sensitivity = analyze_change(prev_input, merged_customer, prev_result, result)

        result["sensitivity_analysis"] = sensitivity
        result["customer_input"] = merged_customer

        # Persist prediction to database asynchronously / synchronously
        db_service.insert_record("predictions", {
            "customer": merged_customer,
            "prediction": {
                "domain": result["domain_prediction"]["primary_domain"],
                "engagement": result["engagement_classification"]["engagement_level"],
                "willingness": result["purchase_willingness"]["willingness_level"],
                "complexity": result["customer_complexity"]["complexity_level"],
                "assigned_agent": result["final_routing"]["assigned_agent"]["agent_id"],
                "required_level": result["final_routing"]["required_agent_level"],
            }
        })

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -------------------------------------------------------------
# MODEL METRICS
# -------------------------------------------------------------
@app.route("/api/model-metrics", methods=["GET"])
def get_model_metrics():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return jsonify({
            "status": "success",
            "metrics": metrics
        }), 200
    return jsonify({
        "status": "error",
        "message": "Model metrics file not found."
    }), 404


# -------------------------------------------------------------
# DATASET SUMMARY
# -------------------------------------------------------------
@app.route("/api/dataset/summary", methods=["GET"])
def get_dataset_summary():
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = json.load(f)
        return jsonify({
            "status": "success",
            "summary": summary
        }), 200
    return jsonify({
        "status": "error",
        "message": "Dataset summary file not found."
    }), 404


# -------------------------------------------------------------
# AGENTS ROSTER
# -------------------------------------------------------------
@app.route("/api/agents", methods=["GET"])
def get_agents():
    agents = db_service.get_all_agents()
    return jsonify({
        "status": "success",
        "count": len(agents),
        "agents": agents
    }), 200


# -------------------------------------------------------------
# SCENARIOS
# -------------------------------------------------------------
@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    return jsonify({
        "status": "success",
        "scenarios": SCENARIOS
    }), 200


# -------------------------------------------------------------
# FEEDBACK
# -------------------------------------------------------------
@app.route("/api/feedback", methods=["POST"])
def record_feedback():
    try:
        data = request.get_json(force=True) or {}
        record = db_service.insert_record("feedback", data)
        return jsonify({
            "status": "success",
            "message": "Feedback recorded successfully.",
            "record": record
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -------------------------------------------------------------
# RETRAIN
# -------------------------------------------------------------
@app.route("/api/train", methods=["POST"])
def retrain():
    try:
        from backend.models.train import train_all_models
        data = request.get_json(silent=True) or {}
        sample_size = int(data.get("sample_size", 20000))
        metrics = train_all_models(sample_size=sample_size)
        routing_engine._load_models()
        return jsonify({
            "status": "success",
            "message": f"Models retrained on {sample_size} records successfully.",
            "metrics": metrics
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
