"""
PolicyBuzar - Core Routing and Prediction Engine
Coordinates the 5 independent classification outputs:
1. Insurance Domain Prediction (with probabilities, primary, secondary, reasoning)
2. Customer Engagement Classification (score, level, most engaged category, visits, time, reasoning)
3. Purchase Willingness Classification (score, level, NLP conversation intent, positive/negative signals)
4. Customer Complexity Classification (score, level, complexity factors, explanation)
5. Final Agent Assignment (matrix combination, escalation rules, intelligent agent roster match)
Exposes individual predictions for LR, DT, RF, KNN, and Ensemble for transparency.
"""

import os
import joblib
import numpy as np
import pandas as pd
from backend.config.policy_config import (
    DOMAINS, AGENT_LEVELS, DECISION_MATRIX, ESCALATION_RULES,
    ENGAGEMENT_WEIGHTS, ENGAGEMENT_THRESHOLDS, WILLINGNESS_THRESHOLDS, COMPLEXITY_THRESHOLDS
)
from backend.services.agent_matcher import match_agent

SAVED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "saved")


class RoutingEngine:
    def __init__(self):
        self.domain_bundle = None
        self.engagement_bundle = None
        self.willingness_bundle = None
        self.complexity_bundle = None
        self.intent_bundle = None
        self._load_models()

    def _load_models(self):
        try:
            self.domain_bundle = joblib.load(os.path.join(SAVED_DIR, "domain_models.joblib"))
            self.engagement_bundle = joblib.load(os.path.join(SAVED_DIR, "engagement_models.joblib"))
            self.willingness_bundle = joblib.load(os.path.join(SAVED_DIR, "willingness_models.joblib"))
            self.complexity_bundle = joblib.load(os.path.join(SAVED_DIR, "complexity_models.joblib"))
            self.intent_bundle = joblib.load(os.path.join(SAVED_DIR, "intent_models.joblib"))
            print("All 5 ML model bundles loaded successfully.")
        except Exception as e:
            print(f"Error loading model bundles: {e}")

    # ------------------------------------------------------------------
    # 1. CONVERSATION INTENT NLP
    # ------------------------------------------------------------------
    def predict_intent(self, message):
        msg = str(message).strip() if message else ""
        if not msg or msg.lower() in ["none", "n/a", ""]:
            return {
                "predicted_intent": "No message",
                "confidence": 1.0,
                "model_predictions": {m: "No message" for m in ["lr", "dt", "rf", "knn", "ensemble"]}
            }

        vec = self.intent_bundle["vectorizer"].transform([msg])
        probs = self.intent_bundle["ensemble"].predict_proba(vec)[0]
        classes = self.intent_bundle["classes"]
        top_idx = int(np.argmax(probs))
        pred_class = classes[top_idx]
        conf = float(probs[top_idx])

        # Get individual model predictions
        individual_preds = {}
        for m in ["lr", "dt", "rf", "knn", "ensemble"]:
            individual_preds[m] = str(self.intent_bundle[m].predict(vec)[0])

        return {
            "predicted_intent": pred_class,
            "confidence": round(conf, 3),
            "model_predictions": individual_preds
        }

    # ------------------------------------------------------------------
    # 2. INSURANCE DOMAIN PREDICTION
    # ------------------------------------------------------------------
    def predict_domain(self, data):
        selected_cat = data.get("selected_category", "None")
        h_views = int(data.get("health_page_views", 0))
        l_views = int(data.get("life_page_views", 0))
        v_views = int(data.get("vehicle_page_views", 0))
        g_views = int(data.get("general_page_views", 0))

        h_time = int(data.get("health_time", 0))
        l_time = int(data.get("life_time", 0))
        v_time = int(data.get("vehicle_time", 0))
        g_time = int(data.get("general_time", 0))

        total_views = h_views + l_views + v_views + g_views
        total_time = h_time + l_time + v_time + g_time

        # If zero activity and no category selected -> Unknown
        if selected_cat in ["None", "", None] and total_views == 0 and total_time == 0:
            return {
                "primary_domain": "Unknown",
                "secondary_domain": None,
                "domain_probabilities": {"Health": 0.25, "Life": 0.25, "Vehicle": 0.25, "General": 0.25},
                "confidence": 0.25,
                "evidence": ["No browsing activity recorded and no explicit category selected."],
                "explanation": "Insufficient behavioral evidence to determine insurance interest.",
                "model_predictions": {m: "Unknown" for m in ["lr", "dt", "rf", "knn", "ensemble"]}
            }

        df_input = pd.DataFrame([{
            "health_page_views": h_views,
            "life_page_views": l_views,
            "vehicle_page_views": v_views,
            "general_page_views": g_views,
            "health_time": h_time,
            "life_time": l_time,
            "vehicle_time": v_time,
            "general_time": g_time,
            "quote_requests": int(data.get("quote_requests", 0)),
            "selected_category": selected_cat
        }])

        proc = self.domain_bundle["preprocessor"].transform(df_input)
        ensemble = self.domain_bundle["ensemble"]
        probs = ensemble.predict_proba(proc)[0]
        classes = self.domain_bundle["classes"]

        prob_dict = {classes[i]: round(float(probs[i]), 3) for i in range(len(classes))}
        # Normalize sum to 100%
        total_p = sum(prob_dict.values())
        if total_p > 0:
            prob_dict = {k: round(v / total_p, 3) for k, v in prob_dict.items()}

        sorted_domains = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_domains[0][0]
        primary_conf = sorted_domains[0][1]
        secondary = sorted_domains[1][0] if len(sorted_domains) > 1 and sorted_domains[1][1] >= 0.15 else None

        # Build evidence
        evidence = []
        if selected_cat in DOMAINS:
            evidence.append(f"Explicit customer selection: '{selected_cat}' (strongest signal)")
        if h_views > 0 or h_time > 0:
            evidence.append(f"Health: {h_views} views ({h_time}s)")
        if l_views > 0 or l_time > 0:
            evidence.append(f"Life: {l_views} views ({l_time}s)")
        if v_views > 0 or v_time > 0:
            evidence.append(f"Vehicle: {v_views} views ({v_time}s)")
        if g_views > 0 or g_time > 0:
            evidence.append(f"General: {g_views} views ({g_time}s)")

        explanation = f"Primary interest in {primary} ({int(primary_conf * 100)}% probability)"
        if secondary:
            explanation += f" with notable secondary interest in {secondary} ({int(sorted_domains[1][1] * 100)}%)."
        else:
            explanation += " based on focused category navigation."

        # Individual model outputs
        individual_preds = {}
        for m in ["lr", "dt", "rf", "knn", "ensemble"]:
            individual_preds[m] = str(self.domain_bundle[m].predict(proc)[0])

        return {
            "primary_domain": primary,
            "secondary_domain": secondary,
            "domain_probabilities": prob_dict,
            "confidence": primary_conf,
            "evidence": evidence,
            "explanation": explanation,
            "model_predictions": individual_preds
        }

    # ------------------------------------------------------------------
    # 3. CUSTOMER ENGAGEMENT CLASSIFICATION
    # ------------------------------------------------------------------
    def predict_engagement(self, data):
        sessions = int(data.get("total_sessions", 1))
        revisits = int(data.get("return_visits", 0))
        quotes = int(data.get("quote_requests", 0))
        callbacks = int(data.get("callback_requests", 0))
        chats = int(data.get("chat_count", 0))

        h_v = int(data.get("health_page_views", 0))
        l_v = int(data.get("life_page_views", 0))
        v_v = int(data.get("vehicle_page_views", 0))
        g_v = int(data.get("general_page_views", 0))

        h_t = int(data.get("health_time", 0))
        l_t = int(data.get("life_time", 0))
        v_t = int(data.get("vehicle_time", 0))
        g_t = int(data.get("general_time", 0))

        total_views = h_v + l_v + v_v + g_v
        total_time = h_t + l_t + v_t + g_t

        # Category with highest time/views
        cat_times = {"Health": h_t, "Life": l_t, "Vehicle": v_t, "General": g_t}
        most_engaged_cat = max(cat_times, key=cat_times.get) if total_time > 0 else "None"
        most_engaged_time = cat_times.get(most_engaged_cat, 0)

        # Weighted Engagement Score (0-100) per PART 5 specification
        w_sessions = min(sessions / 6.0, 1.0) * ENGAGEMENT_WEIGHTS["total_sessions"]
        w_revisits = min(revisits / 4.0, 1.0) * ENGAGEMENT_WEIGHTS["return_visits"]
        w_views = min(total_views / 10.0, 1.0) * ENGAGEMENT_WEIGHTS["relevant_page_views"]
        w_time = min(total_time / 400.0, 1.0) * ENGAGEMENT_WEIGHTS["relevant_time_spent"]
        w_chats = min(chats / 4.0, 1.0) * ENGAGEMENT_WEIGHTS["chat_count"]
        w_quotes = min(quotes / 2.0, 1.0) * ENGAGEMENT_WEIGHTS["quote_activity"]
        w_callbacks = min(callbacks / 2.0, 1.0) * ENGAGEMENT_WEIGHTS["callback_activity"]

        calc_score = round(w_sessions + w_revisits + w_views + w_time + w_chats + w_quotes + w_callbacks, 1)
        calc_score = min(max(calc_score, 0), 100)

        # ML Model Inference
        df_input = pd.DataFrame([{
            "total_sessions": sessions,
            "return_visits": revisits,
            "health_page_views": h_v,
            "life_page_views": l_v,
            "vehicle_page_views": v_v,
            "general_page_views": g_v,
            "health_time": h_t,
            "life_time": l_t,
            "vehicle_time": v_t,
            "general_time": g_t,
            "chat_count": chats,
            "quote_requests": quotes,
            "callback_requests": callbacks
        }])

        proc = self.engagement_bundle["preprocessor"].transform(df_input)
        ensemble = self.engagement_bundle["ensemble"]
        probs = ensemble.predict_proba(proc)[0]
        classes = self.engagement_bundle["classes"]
        top_idx = int(np.argmax(probs))
        ml_level = classes[top_idx]
        conf = float(probs[top_idx])

        # Map score to level if model confidence is close
        if calc_score <= ENGAGEMENT_THRESHOLDS["LOW_MAX"]:
            level = "Low"
        elif calc_score <= ENGAGEMENT_THRESHOLDS["MED_MAX"]:
            level = "Medium"
        else:
            level = "High"

        # Reasoning
        reasons = []
        if revisits >= 2:
            reasons.append(f"{revisits} return visits across {sessions} sessions")
        if total_time >= 200:
            reasons.append(f"Significant time spent exploring ({total_time}s total)")
        if most_engaged_cat != "None":
            reasons.append(f"Dominant attention focused on {most_engaged_cat} ({most_engaged_time}s)")
        if quotes > 0 or callbacks > 0:
            reasons.append(f"Interactive requests: {quotes} quote(s), {callbacks} callback(s)")

        explanation = "; ".join(reasons) if reasons else "Infrequent single-session browsing."

        # Individual model predictions
        individual_preds = {}
        for m in ["lr", "dt", "rf", "knn", "ensemble"]:
            individual_preds[m] = str(self.engagement_bundle[m].predict(proc)[0])

        return {
            "engagement_score": calc_score,
            "engagement_level": level,
            "ml_level": ml_level,
            "confidence": round(conf, 3),
            "most_engaged_category": most_engaged_cat,
            "relevant_visits": revisits,
            "time_spent_seconds": total_time,
            "reasoning": explanation,
            "score_breakdown": {
                "sessions": round(w_sessions, 1),
                "revisits": round(w_revisits, 1),
                "page_views": round(w_views, 1),
                "time_spent": round(w_time, 1),
                "chat": round(w_chats, 1),
                "quote": round(w_quotes, 1),
                "callback": round(w_callbacks, 1)
            },
            "model_predictions": individual_preds
        }

    # ------------------------------------------------------------------
    # 4. PURCHASE WILLINGNESS CLASSIFICATION
    # ------------------------------------------------------------------
    def predict_willingness(self, data, intent_info=None):
        if intent_info is None:
            intent_info = self.predict_intent(data.get("customer_message", ""))

        intent = intent_info.get("predicted_intent", "No message")
        quotes = int(data.get("quote_requests", 0))
        callbacks = int(data.get("callback_requests", 0))
        revisits = int(data.get("return_visits", 0))
        sessions = int(data.get("total_sessions", 1))
        chats = int(data.get("chat_count", 0))

        h_t = int(data.get("health_time", 0))
        l_t = int(data.get("life_time", 0))
        v_t = int(data.get("vehicle_time", 0))
        g_t = int(data.get("general_time", 0))
        total_time = h_t + l_t + v_t + g_t

        # Signals
        positive_signals = []
        negative_signals = []

        if quotes > 0:
            positive_signals.append(f"{quotes} quote request(s) initiated")
        if callbacks > 0:
            positive_signals.append(f"{callbacks} callback request(s) booked")
        if intent == "Ready to buy":
            positive_signals.append("Explicit high purchase intention in conversation")
        elif intent == "Interested":
            positive_signals.append("Expressed active product interest in conversation")
        elif intent in ["Price objection", "Trust objection"]:
            negative_signals.append(f"Expressed objection: {intent}")
        elif intent == "Unwilling":
            negative_signals.append("Customer explicitly indicated lack of interest")

        if quotes == 0 and callbacks == 0:
            negative_signals.append("No quote or callback requested yet")

        # ML Model Inference
        df_input = pd.DataFrame([{
            "quote_requests": quotes,
            "callback_requests": callbacks,
            "return_visits": revisits,
            "total_sessions": sessions,
            "health_time": h_t,
            "life_time": l_t,
            "vehicle_time": v_t,
            "general_time": g_t,
            "chat_count": chats,
            "conversation_intent": intent
        }])

        proc = self.willingness_bundle["preprocessor"].transform(df_input)
        ensemble = self.willingness_bundle["ensemble"]
        probs = ensemble.predict_proba(proc)[0]
        classes = self.willingness_bundle["classes"]
        top_idx = int(np.argmax(probs))
        ml_level = classes[top_idx]
        conf = float(probs[top_idx])

        # Calculate calibrated willingness score (0-100)
        # Quote: 30, Callback: 25, Intent: 25, Revisits: 10, Time: 10
        intent_scores = {
            "Ready to buy": 25,
            "Interested": 18,
            "Needs guidance": 10,
            "General enquiry": 6,
            "No message": 4,
            "Price objection": 2,
            "Trust objection": 1,
            "Unwilling": -15
        }
        score = (
            min(quotes / 2.0, 1.0) * 30 +
            min(callbacks / 1.0, 1.0) * 25 +
            intent_scores.get(intent, 5) +
            min(revisits / 3.0, 1.0) * 10 +
            min(total_time / 350.0, 1.0) * 10
        )
        score = round(min(max(score, 0), 100), 1)

        if score <= WILLINGNESS_THRESHOLDS["LOW_MAX"]:
            level = "Low"
        elif score <= WILLINGNESS_THRESHOLDS["MED_MAX"]:
            level = "Medium"
        else:
            level = "High"

        # Explicit "Ready to buy" boost per business rule
        if intent == "Ready to buy" and (quotes > 0 or callbacks > 0):
            level = "High"
            score = max(score, 75.0)

        explanation = (
            f"Willingness is {level} ({score}/100). Conversation intent: '{intent}'. "
            f"Key drivers: {', '.join(positive_signals) if positive_signals else 'No positive purchasing actions'}."
        )

        individual_preds = {}
        for m in ["lr", "dt", "rf", "knn", "ensemble"]:
            individual_preds[m] = str(self.willingness_bundle[m].predict(proc)[0])

        return {
            "willingness_score": score,
            "willingness_level": level,
            "ml_level": ml_level,
            "confidence": round(conf, 3),
            "conversation_intent": intent,
            "positive_signals": positive_signals,
            "negative_signals": negative_signals,
            "explanation": explanation,
            "model_predictions": individual_preds
        }

    # ------------------------------------------------------------------
    # 5. CUSTOMER COMPLEXITY CLASSIFICATION
    # ------------------------------------------------------------------
    def predict_complexity(self, data):
        doubts = int(data.get("doubts", 0))
        questions = int(data.get("questions", 0))
        chats = int(data.get("chat_count", 0))
        risk = int(data.get("risk_score", 20))
        prev_failed = bool(data.get("previous_agent_failed", False))
        existing_pol = bool(data.get("existing_policy", False))

        h_v = int(data.get("health_page_views", 0))
        l_v = int(data.get("life_page_views", 0))
        v_v = int(data.get("vehicle_page_views", 0))
        g_v = int(data.get("general_page_views", 0))

        cats_active = sum([h_v > 0, l_v > 0, v_v > 0, g_v > 0])

        # Complexity Factors & Missing Information
        factors = []
        if prev_failed:
            factors.append("Previous agent interaction failed (Immediate escalation risk)")
        if cats_active > 1:
            factors.append(f"Cross-category interest across {cats_active} distinct domains")
        if doubts >= 3:
            factors.append(f"Elevated doubt count ({doubts} recorded doubts)")
        if questions >= 4:
            factors.append(f"High inquiry volume ({questions} product questions)")
        if chats >= 4:
            factors.append(f"Substantial chat volume ({chats} sessions)")
        if risk >= 60:
            factors.append(f"High case risk score ({risk}/100)")

        missing_info = []
        if data.get("monthly_income") is None or str(data.get("monthly_income")) in ["", "nan"]:
            missing_info.append("Monthly income not disclosed")
        if data.get("credit_score") is None or str(data.get("credit_score")) in ["", "nan"]:
            missing_info.append("Credit score unavailable")

        # ML Model Inference
        df_input = pd.DataFrame([{
            "doubts": doubts,
            "questions": questions,
            "chat_count": chats,
            "risk_score": risk,
            "health_page_views": h_v,
            "life_page_views": l_v,
            "vehicle_page_views": v_v,
            "general_page_views": g_v,
            "previous_agent_failed": int(prev_failed),
            "existing_policy": int(existing_pol)
        }])

        proc = self.complexity_bundle["preprocessor"].transform(df_input)
        ensemble = self.complexity_bundle["ensemble"]
        probs = ensemble.predict_proba(proc)[0]
        classes = self.complexity_bundle["classes"]
        top_idx = int(np.argmax(probs))
        ml_level = classes[top_idx]
        conf = float(probs[top_idx])

        # Calculated Complexity Score (0-100)
        # Category count: 20, Doubts: 25, Questions: 25, Prev Failed: 20, Chat: 10
        score = (
            min(max(cats_active - 1, 0) / 2.0, 1.0) * 20 +
            min(doubts / 5.0, 1.0) * 25 +
            min(questions / 6.0, 1.0) * 25 +
            (20 if prev_failed else 0) +
            min(chats / 6.0, 1.0) * 10
        )
        score = round(min(max(score, 0), 100), 1)

        if score <= COMPLEXITY_THRESHOLDS["LOW_MAX"]:
            level = "Low"
        elif score <= COMPLEXITY_THRESHOLDS["MED_MAX"]:
            level = "Medium"
        else:
            level = "High"

        # Explicit overrides: previous agent failed or very high doubts/questions forces High
        if prev_failed or (doubts >= 5 and questions >= 6):
            level = "High"
            score = max(score, 70.0)

        explanation = (
            f"Complexity level is {level} ({score}/100). "
            f"{'Key drivers: ' + '; '.join(factors) if factors else 'Standard straightforward single-line policy request.'}"
        )

        individual_preds = {}
        for m in ["lr", "dt", "rf", "knn", "ensemble"]:
            individual_preds[m] = str(self.complexity_bundle[m].predict(proc)[0])

        return {
            "complexity_score": score,
            "complexity_level": level,
            "ml_level": ml_level,
            "confidence": round(conf, 3),
            "main_complexity_factors": factors,
            "missing_information": missing_info,
            "explanation": explanation,
            "model_predictions": individual_preds
        }

    # ------------------------------------------------------------------
    # 6. FINAL AGENT ASSIGNMENT ENGINE
    # ------------------------------------------------------------------
    def assign_agent(self, data, domain_res, eng_res, will_res, comp_res):
        will_lvl = will_res["willingness_level"]
        comp_lvl = comp_res["complexity_level"]
        prev_failed = bool(data.get("previous_agent_failed", False))
        lang = data.get("language", "English")
        domain = domain_res["primary_domain"]
        if domain == "Unknown":
            domain = "General"

        # Decision Matrix & Override Resolution (PART 8 & PART 9)
        escalation_triggered = False
        escalation_reason = ""

        if prev_failed:
            required_level = AGENT_LEVELS["SENIOR"]
            escalation_triggered = True
            escalation_reason = "Overridden to Senior Expert Agent: Previous agent interaction failed."
        elif comp_lvl == "High":
            required_level = AGENT_LEVELS["SENIOR"]
            escalation_triggered = True
            escalation_reason = "Routed to Senior Expert Agent: High case complexity requires senior specialist."
        else:
            # Query the central Decision Matrix
            required_level = DECISION_MATRIX.get((will_lvl, comp_lvl), AGENT_LEVELS["EXPERT"])
            escalation_reason = f"Decision Matrix ({will_lvl} Willingness x {comp_lvl} Complexity) -> {required_level}."

        # Intelligent Roster Match
        agent_match = match_agent(required_level, domain, lang)

        # Combined Reasoning
        assignment_summary = (
            f"Customer profile indicates {domain_res['primary_domain']} domain, "
            f"{eng_res['engagement_level']} engagement ({eng_res['engagement_score']}/100), "
            f"{will_lvl} purchase willingness ({will_res['willingness_score']}/100), "
            f"and {comp_lvl} customer complexity ({comp_res['complexity_score']}/100). "
            f"{escalation_reason} Assigned Agent: {agent_match['agent_name']} ({agent_match['agent_id']})."
        )

        return {
            "required_agent_level": required_level,
            "escalation_triggered": escalation_triggered,
            "escalation_reason": escalation_reason,
            "assigned_agent": agent_match,
            "assignment_summary": assignment_summary
        }

    # ------------------------------------------------------------------
    # FULL PREDICTION PIPELINE
    # ------------------------------------------------------------------
    def process_customer(self, customer_data):
        # 1. Conversation Intent NLP
        intent_res = self.predict_intent(customer_data.get("customer_message", ""))

        # 2. Domain Prediction
        domain_res = self.predict_domain(customer_data)

        # 3. Engagement Classification
        engagement_res = self.predict_engagement(customer_data)

        # 4. Purchase Willingness Classification
        willingness_res = self.predict_willingness(customer_data, intent_res)

        # 5. Customer Complexity Classification
        complexity_res = self.predict_complexity(customer_data)

        # 6. Final Agent Assignment
        routing_res = self.assign_agent(customer_data, domain_res, engagement_res, willingness_res, complexity_res)

        return {
            "domain_prediction": domain_res,
            "engagement_classification": engagement_res,
            "purchase_willingness": willingness_res,
            "customer_complexity": complexity_res,
            "conversation_intent": intent_res,
            "final_routing": routing_res
        }


# Singleton instance
routing_engine = RoutingEngine()

