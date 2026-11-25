"""
PolicyBuzar - Feature Sensitivity Tracker
Analyzes real-time field changes between consecutive customer states:
- Previous value vs New value
- Which predictions/models are genuinely affected
- Previous classification vs Updated classification
- Plain-English explanation of why the assignment changed (or why it remained stable)
"""

FIELD_DOMAIN_MAP = {
    # Customer profile
    "age": {"targets": ["Customer Profile / Assistance Context"], "reason": "Age informs assistance requirements but alone does not alter agent tier."},
    "monthly_income": {"targets": ["Affordability Context"], "reason": "Income provides financial context but does not directly govern willingness or tier."},
    "credit_score": {"targets": ["Financial Support Assessment"], "reason": "Credit score provides underwriting context without penalizing routing."},
    "marital_status": {"targets": ["Coverage Needs"], "reason": "Marital status informs family coverage recommendations."},
    "dependents": {"targets": ["Coverage Needs"], "reason": "Dependents inform coverage magnitude (e.g., family floater sizing)."},
    "existing_policy": {"targets": ["Customer Complexity", "Coverage Context"], "reason": "Existing policy alters portfolio complexity and portability."},
    "selected_category": {"targets": ["Insurance Domain Prediction"], "reason": "Explicit category selection is the primary driver of domain classification."},

    # Customer behaviour
    "health_page_views": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Health page views increase Health domain weight and engagement score."},
    "life_page_views": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Life page views increase Life domain weight and engagement score."},
    "vehicle_page_views": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Vehicle views increase Vehicle domain weight and engagement score."},
    "general_page_views": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "General views increase General domain weight and engagement score."},
    "health_time": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Category dwell time measures focused domain interest."},
    "life_time": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Category dwell time measures focused domain interest."},
    "vehicle_time": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Category dwell time measures focused domain interest."},
    "general_time": {"targets": ["Insurance Domain", "Customer Engagement"], "reason": "Category dwell time measures focused domain interest."},

    # Engagement signals
    "total_sessions": {"targets": ["Customer Engagement"], "reason": "Total sessions directly scale engagement frequency score."},
    "return_visits": {"targets": ["Customer Engagement", "Purchase Willingness"], "reason": "Return visits demonstrate persistent interest and higher intent."},
    "quote_requests": {"targets": ["Purchase Willingness"], "reason": "Quote submission is a direct high-intent purchasing indicator."},
    "callback_requests": {"targets": ["Purchase Willingness"], "reason": "Callback request signifies immediate purchase consultation readiness."},
    "chat_count": {"targets": ["Customer Engagement", "Customer Complexity"], "reason": "High chat activity reflects engagement; multiple chats with doubts raise complexity."},
    "doubts": {"targets": ["Customer Complexity"], "reason": "Doubts directly elevate complexity score and product assistance needs."},
    "questions": {"targets": ["Customer Complexity"], "reason": "Questions increase case complexity and need for consultative agents."},
    "risk_score": {"targets": ["Customer Complexity", "Service & Underwriting Risk", "Final Agent Assignment"], "reason": "Risk score directly scales complexity, updates KYC verification tier, and triggers Senior escalation when >= 75."},
    "previous_agent_failed": {"targets": ["Customer Complexity", "Final Agent Assignment"], "reason": "Previous agent failure triggers an immediate mandatory Senior Expert escalation override."},
    "language": {"targets": ["Final Agent Assignment (Agent Matching)"], "reason": "Language preferences filter agent roster for native-language routing."},
    "customer_message": {"targets": ["Conversation Intent NLP", "Purchase Willingness"], "reason": "NLP classifier extracts semantic intent and purchase readiness."}
}


def analyze_change(prev_input, new_input, prev_result, new_result):
    if not prev_input or not new_input:
        return None

    # Detect changed fields
    changed_fields = []
    for k in new_input:
        if k in prev_input and prev_input[k] != new_input[k]:
            changed_fields.append({
                "field": k,
                "prev_val": prev_input[k],
                "new_val": new_input[k]
            })

    if not changed_fields:
        return None

    # Pick the most significant changed field
    primary_change = changed_fields[0]
    field = primary_change["field"]
    field_info = FIELD_DOMAIN_MAP.get(field, {"targets": ["General Model"], "reason": "Input value modified."})

    # Track classification shifts
    prev_agent = prev_result.get("final_routing", {}).get("required_agent_level") if prev_result else None
    new_agent = new_result.get("final_routing", {}).get("required_agent_level") if new_result else None

    prev_domain = prev_result.get("domain_prediction", {}).get("primary_domain") if prev_result else None
    new_domain = new_result.get("domain_prediction", {}).get("primary_domain") if new_result else None

    prev_will = prev_result.get("purchase_willingness", {}).get("willingness_level") if prev_result else None
    new_will = new_result.get("purchase_willingness", {}).get("willingness_level") if new_result else None

    prev_comp = prev_result.get("customer_complexity", {}).get("complexity_level") if prev_result else None
    new_comp = new_result.get("customer_complexity", {}).get("complexity_level") if new_result else None

    prev_eng = prev_result.get("engagement_classification", {}).get("engagement_level") if prev_result else None
    new_eng = new_result.get("engagement_classification", {}).get("engagement_level") if new_result else None

    shifts = []
    if prev_domain != new_domain:
        shifts.append(f"Domain shifted: {prev_domain} → {new_domain}")
    if prev_will != new_will:
        shifts.append(f"Willingness shifted: {prev_will} → {new_will}")
    if prev_comp != new_comp:
        shifts.append(f"Complexity shifted: {prev_comp} → {new_comp}")
    if prev_eng != new_eng:
        shifts.append(f"Engagement shifted: {prev_eng} → {new_eng}")
    if prev_agent != new_agent:
        shifts.append(f"Assigned Agent Level shifted: {prev_agent} → {new_agent}")

    if shifts:
        impact_summary = "Decision boundary crossed: " + "; ".join(shifts) + "."
    else:
        impact_summary = f"No classification shift. '{field}' changed within existing boundary tolerances."

    return {
        "changed_field": field,
        "previous_value": primary_change["prev_val"],
        "new_value": primary_change["new_val"],
        "all_changed_fields": [c["field"] for c in changed_fields],
        "predictions_affected": field_info["targets"],
        "previous_assignment": prev_agent,
        "updated_assignment": new_agent,
        "impact_summary": impact_summary,
        "explanation": field_info["reason"]
    }

