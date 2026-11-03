from predictor import CustomerAI
from router import AgentRouter


BASE = {
    "age": 35,
    "income_monthly": 60000,
    "credit_score": 720,
    "marital_status": "married",
    "dependents": 2,
    "existing_policy": "none",
    "selected_category": "none",
    "health_page_views": 10,
    "life_page_views": 1,
    "vehicle_page_views": 0,
    "general_page_views": 1,
    "health_time_seconds": 500,
    "life_time_seconds": 30,
    "vehicle_time_seconds": 0,
    "general_time_seconds": 20,
    "health_comparisons": 0,
    "life_comparisons": 0,
    "vehicle_comparisons": 0,
    "general_comparisons": 0,
    "total_sessions": 4,
    "return_visits": 3,
    "quote_requests": 0,
    "callback_requests": 0,
    "chat_count": 1,
}


def customer(**changes):
    result = dict(BASE)
    result.update(changes)
    return result


SCENARIOS = [
    ("health", customer(health_page_views=15, health_time_seconds=800, health_comparisons=5), "I want health insurance"),
    ("life", customer(life_page_views=15, life_time_seconds=800, life_comparisons=5), "I want to buy life insurance"),
    ("vehicle", customer(vehicle_page_views=15, vehicle_time_seconds=800, vehicle_comparisons=5), "Show me vehicle insurance plans"),
    ("general", customer(general_page_views=15, general_time_seconds=800, general_comparisons=5), "Tell me about insurance"),
    ("health without selection", customer(health_page_views=15, health_time_seconds=800, health_comparisons=3), "Tell me about health insurance"),
    ("life without selection", customer(life_page_views=15, life_time_seconds=800, life_comparisons=3), "Tell me about life insurance"),
    ("vehicle without selection", customer(vehicle_page_views=15, vehicle_time_seconds=800, vehicle_comparisons=3), "Tell me about vehicle insurance"),
    ("general without selection", customer(general_page_views=15, general_time_seconds=800, general_comparisons=3), "Tell me about insurance"),
    ("young high-income not interested", customer(age=25, income_monthly=250000, credit_score=780), "I am not interested in insurance"),
    ("elderly low-income purchase", customer(age=80, income_monthly=12000, dependents=3, quote_requests=2, callback_requests=1, chat_count=5), "I strongly want to buy health insurance"),
    ("high-income not interested", customer(income_monthly=500000, credit_score=820), "I do not want insurance"),
    ("complex senior", customer(existing_policy="multiple", dependents=4, total_sessions=12, return_visits=11, quote_requests=3, callback_requests=2, chat_count=15, health_comparisons=5, life_comparisons=5, vehicle_comparisons=2), "I need a senior agent to help compare several policies"),
]


if __name__ == "__main__":
    ai = CustomerAI()
    router = AgentRouter()
    for name, data, message in SCENARIOS:
        analysis = ai.analyze(data, message)
        assignment = router.assign(analysis)
        agent = assignment.get("agent") or {}
        print(
            f"{name}: domain={analysis['domain']} intent={analysis['intent']} "
            f"engagement={analysis['engagement']} purchase={analysis['purchase_intent']} "
            f"complexity={analysis['complexity']} credit_score={analysis['credit_score']} "
            f"required={assignment['required_level']} "
            f"assigned={agent.get('name', 'none')} ({agent.get('role', 'none')})"
        )
