"""
PolicyBuzar - Central Business Policy Configuration
Centralizes all business rules, scoring weights, classification thresholds,
agent decision matrices, and intent definitions. No hardcoded logic in components.
"""

# Supported Insurance Categories / Domains
DOMAINS = ["Health", "Life", "Vehicle", "General"]

# Agent Levels
AGENT_LEVELS = {
    "INTERN": "Intern Agent",
    "EXPERT": "Expert Agent",
    "SENIOR": "Senior Expert Agent"
}

# Supported Indian Languages for Intelligent Routing
LANGUAGES = [
    "English", "Hindi", "Telugu", "Tamil", "Kannada", "Marathi", "Bengali", "Gujarati"
]

# Conversation Intents
CONVERSATION_INTENTS = [
    "Ready to buy",
    "Interested",
    "Needs guidance",
    "Price objection",
    "Trust objection",
    "Unwilling",
    "General enquiry",
    "No message"
]

# Classification Thresholds (0 - 100 scale)
ENGAGEMENT_THRESHOLDS = {
    "LOW_MAX": 30,
    "MED_MAX": 65
}

WILLINGNESS_THRESHOLDS = {
    "LOW_MAX": 30,
    "MED_MAX": 65
}

COMPLEXITY_THRESHOLDS = {
    "LOW_MAX": 30,
    "MED_MAX": 65
}

# Engagement Feature Weights (sum to 100)
ENGAGEMENT_WEIGHTS = {
    "total_sessions": 15,
    "return_visits": 20,
    "relevant_page_views": 20,
    "relevant_time_spent": 15,
    "chat_count": 10,
    "quote_activity": 10,
    "callback_activity": 10
}

# Final Agent Decision Matrix (Willingness x Complexity -> Agent Tier)
# As requested in PART 9 of the specification
DECISION_MATRIX = {
    ("High", "Low"): AGENT_LEVELS["INTERN"],
    ("High", "Medium"): AGENT_LEVELS["EXPERT"],
    ("High", "High"): AGENT_LEVELS["SENIOR"],
    ("Medium", "Low"): AGENT_LEVELS["EXPERT"],
    ("Medium", "Medium"): AGENT_LEVELS["EXPERT"],
    ("Medium", "High"): AGENT_LEVELS["SENIOR"],
    ("Low", "Low"): AGENT_LEVELS["EXPERT"],
    ("Low", "Medium"): AGENT_LEVELS["EXPERT"],
    ("Low", "High"): AGENT_LEVELS["SENIOR"],
}

# Senior Escalation Overrides (PART 8 & PART 9)
ESCALATION_RULES = {
    "previous_agent_failed": True,     # Forces Senior Expert Agent
    "unresolved_complaint": True,      # Forces Senior Expert Agent
    "high_service_risk": 80,           # Risk score >= 80 indicates escalated service risk
    "min_senior_experience_years": 4   # Minimum experience for Senior Agent
}

# Default initial customer values
DEFAULT_CUSTOMER = {
    "age": 32,
    "monthly_income": 65000,
    "credit_score": 720,
    "marital_status": "Married",
    "dependents": 1,
    "existing_policy": False,
    "selected_category": "Health",
    "health_page_views": 4,
    "life_page_views": 0,
    "vehicle_page_views": 0,
    "general_page_views": 0,
    "health_time": 240,
    "life_time": 0,
    "vehicle_time": 0,
    "general_time": 0,
    "total_sessions": 3,
    "return_visits": 2,
    "quote_requests": 1,
    "callback_requests": 1,
    "chat_count": 1,
    "doubts": 0,
    "questions": 1,
    "risk_score": 25,
    "previous_agent_failed": False,
    "language": "English",
    "customer_message": "I want to purchase a family health insurance plan today."
}

