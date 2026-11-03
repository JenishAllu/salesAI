
import requests
import json

url = "http://127.0.0.1:5000/analyze"

customer = {
    "age": 31,
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

    "health_comparisons": 3,
    "life_comparisons": 0,
    "vehicle_comparisons": 0,
    "general_comparisons": 0,

    "total_sessions": 4,
    "return_visits": 3,
    "quote_requests": 1,
    "callback_requests": 1,
    "chat_count": 3
}

payload = {
    "customer": customer,
    "message": "I want to compare health insurance for my parents.",
    "language": "Telugu"
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
