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
import datetime
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
        "engine": "salesIntelAi Dynamic Multi-Model AI Routing Engine v2.0"
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

        # Also log active assignment into assignments collection for live agent history
        assigned_agent = result["final_routing"]["assigned_agent"]
        if assigned_agent and assigned_agent.get("agent_id") not in ["QUEUE-001", "OVERFLOW-001"]:
            case_id = f"LIVE-{assigned_agent.get('agent_id')}-{int(datetime.datetime.now().timestamp()) % 100000}"
            db_service.insert_record("assignments", {
                "case_id": case_id,
                "customer_id": f"CUST{int(datetime.datetime.now().timestamp()) % 100000}",
                "customer_name": f"Live Customer ({result['domain_prediction']['primary_domain']})",
                "agent_id": assigned_agent.get("agent_id"),
                "agent_name": assigned_agent.get("agent_name"),
                "agent_level": assigned_agent.get("agent_level"),
                "domain": result["domain_prediction"]["primary_domain"],
                "complexity": result["customer_complexity"]["complexity_level"],
                "date_assigned": datetime.date.today().isoformat(),
                "outcome": "in_progress",
                "outcome_notes": "Assigned dynamically via simulator.",
                "escalated_to": None,
                "customer_data": merged_customer
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
# AGENTS ROSTER & HISTORY
# -------------------------------------------------------------
@app.route("/api/agents", methods=["GET"])
def get_agents():
    agents = db_service.get_all_agents()
    return jsonify({
        "status": "success",
        "count": len(agents),
        "agents": agents
    }), 200


@app.route("/api/agents/<agent_id>/history", methods=["GET"])
def get_agent_history(agent_id):
    agent = db_service.get_agent_by_id(agent_id)
    if not agent:
        return jsonify({"status": "error", "message": f"Agent {agent_id} not found."}), 404
    history = db_service.get_agent_history(agent_id)
    return jsonify({
        "status": "success",
        "agent": agent,
        "count": len(history),
        "history": history
    }), 200


@app.route("/api/agents/<agent_id>/outcome", methods=["POST"])
def record_agent_outcome(agent_id):
    try:
        from backend.services.agent_matcher import match_agent
        from backend.models.train import train_all_models

        body = request.get_json(force=True) or {}
        case_id = body.get("case_id")
        outcome = body.get("outcome", "succeeded").lower()  # "succeeded" or "failed"
        notes = body.get("notes", "")

        agent = db_service.get_agent_by_id(agent_id)
        if not agent:
            return jsonify({"status": "error", "message": f"Agent {agent_id} not found."}), 404

        # Update assignment outcome in database
        updated_case = db_service.update_case_outcome(agent_id, case_id, outcome, notes)
        if not updated_case:
            return jsonify({"status": "error", "message": f"Case {case_id} not found."}), 404

        cust_data = dict(updated_case.get("customer_data", DEFAULT_CUSTOMER))
        escalation_info = None
        retrained = False

        if outcome == "failed":
            # Current agent level
            curr_lvl = agent.get("agent_level", "Intern Agent")
            comp = updated_case.get("complexity", "Low")
            dom = updated_case.get("domain", "Health")
            lang = cust_data.get("language", "English")

            # Determine higher agent tier
            if curr_lvl == "Intern Agent":
                higher_tier = "Expert Agent" if comp != "High" else "Senior Expert Agent"
            elif curr_lvl == "Expert Agent":
                higher_tier = "Senior Expert Agent"
            else:
                higher_tier = "Senior Expert Agent"

            # Customer has failed interaction -> triggers previous_agent_failed escalation
            cust_data["previous_agent_failed"] = True

            # Match qualified higher agent
            higher_agent = match_agent(higher_tier, dom, lang)

            # Update the case with escalation data
            db_service.update_agent(agent_id, {
                "performance_rating": max(4.0, round(float(agent.get("performance_rating", 4.5)) - 0.05, 2))
            })

            # Create new escalated assignment case for the higher agent
            new_case_id = f"ESC-{case_id}-{int(datetime.datetime.now().timestamp()) % 10000}"
            db_service.insert_record("assignments", {
                "case_id": new_case_id,
                "customer_id": updated_case.get("customer_id", "CUST10099"),
                "customer_name": updated_case.get("customer_name", "Customer"),
                "agent_id": higher_agent["agent_id"],
                "agent_name": higher_agent["agent_name"],
                "agent_level": higher_agent["agent_level"],
                "domain": dom,
                "complexity": comp,
                "date_assigned": datetime.date.today().isoformat(),
                "outcome": "in_progress",
                "outcome_notes": f"Escalated from {agent['agent_name']} ({agent_id} - {curr_lvl}). Reason: {notes or 'Previous agent failed.'}",
                "escalated_from": agent_id,
                "customer_data": cust_data
            })

            # Mark previous case as escalated
            db_service.update_case_outcome(
                agent_id,
                case_id,
                "failed",
                notes=f"Interaction failed. Escalated to {higher_agent['agent_name']} ({higher_agent['agent_id']} - {higher_agent['agent_level']})."
            )

            # Retrain ML models on the updated dataset / feedback
            try:
                train_all_models(sample_size=10000)
                routing_engine._load_models()
                retrained = True
            except Exception as e:
                print(f"Retraining error: {e}")

            escalation_info = {
                "case_id": case_id,
                "customer_id": updated_case.get("customer_id"),
                "customer_name": updated_case.get("customer_name"),
                "previous_agent": {
                    "id": agent["agent_id"],
                    "name": agent["agent_name"],
                    "level": curr_lvl
                },
                "new_agent": higher_agent,
                "escalated_tier": higher_tier,
                "escalated_case_id": new_case_id,
                "customer_data": cust_data,
                "reason": f"Agent {agent['agent_name']} failed resolution. Customer escalated to higher tier ({higher_tier}) assigned to {higher_agent['agent_name']} ({higher_agent['agent_id']})."
            }
        else:
            # Success: update agent performance rating and increment resolved count
            db_service.update_agent(agent_id, {
                "performance_rating": min(4.98, round(float(agent.get("performance_rating", 4.5)) + 0.02, 2)),
                "assigned_customer_count": int(agent.get("assigned_customer_count", 20)) + 1
            })

        # Return updated history
        updated_history = db_service.get_agent_history(agent_id)
        updated_agent = db_service.get_agent_by_id(agent_id)

        return jsonify({
            "status": "success",
            "message": f"Case outcome updated to '{outcome}'. " + ("Customer escalated and models retrained." if outcome == "failed" else "Case marked as completed."),
            "outcome": outcome,
            "escalation": escalation_info,
            "retrained": retrained,
            "agent": updated_agent,
            "history": updated_history
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


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
