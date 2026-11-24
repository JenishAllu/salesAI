"""
PolicyBuzar - Synthetic Dataset & Agent Roster Generator
Generates:
1. >= 100,000 realistic customer records with rich correlations, realistic noise,
   controlled missing values, and target labels for:
   - insurance_domain (Health, Life, Vehicle, General)
   - engagement_level (Low, Medium, High)
   - purchase_willingness (Low, Medium, High)
   - customer_complexity (Low, Medium, High)
   - conversation_intent (8 classes)
   - required_agent_level (Intern, Expert, Senior Expert)
2. 40 realistic synthetic agents with unique IDs (AG101 - AG140).
3. dataset_summary.json report.
"""

import os
import json
import random
import numpy as np
import pandas as pd

# Set fixed random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOMERS_CSV = os.path.join(DATA_DIR, "synthetic_customers.csv")
AGENTS_CSV = os.path.join(DATA_DIR, "synthetic_agents.csv")
SUMMARY_JSON = os.path.join(DATA_DIR, "dataset_summary.json")

LANGUAGES = ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Marathi", "Bengali", "Gujarati"]
DOMAINS = ["Health", "Life", "Vehicle", "General"]
MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed"]
CATEGORIES_CHOICES = ["None", "Health", "Life", "Vehicle", "General"]

INTENT_TEMPLATES = {
    "Ready to buy": [
        "I want to purchase health insurance today.",
        "Ready to buy the policy now, please send payment link.",
        "I want to finalize the term life policy right away.",
        "Please proceed with my vehicle insurance policy issuance.",
        "Ready to pay the annual premium today, please assist with payment.",
        "I have chosen the 1 crore term plan, let's complete the purchase.",
        "Need to buy this comprehensive car cover immediately before expiry."
    ],
    "Interested": [
        "I am looking for a comprehensive medical coverage for my family.",
        "Interested in term life insurance for 1 crore cover.",
        "Looking for car insurance quotes for my new sedan.",
        "Interested in buying health insurance for my senior parents.",
        "Exploring life insurance options with good claim settlement ratio.",
        "Want to check coverage details for critical illnesses."
    ],
    "Needs guidance": [
        "Which policy is better for senior citizens?",
        "Can you help me choose between term life and ULIP?",
        "Not sure which health insurance plan covers maternity without waiting period.",
        "Need comparison between Plan A and Plan B benefits.",
        "Could you explain the difference between comprehensive and third party car insurance?",
        "Confused about deductible vs co-pay in health policies."
    ],
    "Price objection": [
        "The premium is too expensive for my budget.",
        "Your rates are higher than competitors in the market.",
        "Can I get a discount on the annual premium?",
        "The monthly premium exceeds what I planned to spend.",
        "Is there a cheaper version of this plan with essential coverage?",
        "Too costly compared to the quote I received yesterday."
    ],
    "Trust objection": [
        "I don't trust private insurance companies with claim settlement.",
        "Will my claim actually be settled or will it be rejected on technicalities?",
        "I read negative reviews about delay in cashless hospital approvals.",
        "Are there hidden clauses and exclusions in this policy document?",
        "How can I be sure your claim settlement ratio is genuine?"
    ],
    "Unwilling": [
        "I don't want insurance at this time.",
        "Stop calling me, I am not interested in buying anything.",
        "I did not request any quote, please remove my number.",
        "Not planning to buy any insurance policy right now.",
        "Just randomly clicked, not looking to buy anything."
    ],
    "General enquiry": [
        "What are your customer support office hours?",
        "How long does policy issuance take after payment?",
        "Can I pay via UPI or credit card EMI?",
        "What documents are required for digital KYC verification?",
        "Do you have network cashless hospitals in Bangalore and Hyderabad?"
    ],
    "No message": [
        "",
        " ",
        "N/A",
        "None"
    ]
}


def generate_customers(num_records=100000):
    print(f"Generating {num_records} synthetic customer records...")

    # Customer Profiles
    ages = np.random.randint(18, 76, size=num_records)
    # Realistic log-normal income in INR (mean ~65k, range ~15k to ~450k)
    incomes = np.round(np.random.lognormal(mean=11.0, sigma=0.6, size=num_records)).astype(int)
    incomes = np.clip(incomes, 15000, 500000)

    # Credit scores (normal distribution around 710, range 320 to 850)
    credit_scores = np.round(np.random.normal(loc=710, scale=80, size=num_records)).astype(int)
    credit_scores = np.clip(credit_scores, 320, 850)

    marital_status = np.random.choice(MARITAL_STATUSES, size=num_records, p=[0.35, 0.55, 0.06, 0.04])
    dependents = np.where(marital_status == "Single", np.random.choice([0, 1, 2], size=num_records, p=[0.75, 0.20, 0.05]),
                          np.random.choice([0, 1, 2, 3, 4], size=num_records, p=[0.15, 0.40, 0.30, 0.12, 0.03]))
    existing_policy = np.random.choice([True, False], size=num_records, p=[0.42, 0.58])
    languages = np.random.choice(LANGUAGES, size=num_records, p=[0.40, 0.25, 0.10, 0.08, 0.05, 0.05, 0.04, 0.03])

    # Customer Persona Archetypes to generate realistic correlations
    # 0: Direct Willing Buyer (Intern candidate)
    # 1: Multi-category Comparer (Expert candidate)
    # 2: Hesitant / Price Sensitive (Expert candidate)
    # 3: High-Complexity / Multi-domain (Senior candidate)
    # 4: Escalation / Previous Failure (Senior candidate)
    # 5: Casual Low-engagement Browser (Nurture / Low)
    archetypes = np.random.choice([0, 1, 2, 3, 4, 5], size=num_records, p=[0.24, 0.22, 0.18, 0.15, 0.06, 0.15])

    # Initialize behavioral arrays
    selected_category = []
    health_views = np.zeros(num_records, dtype=int)
    life_views = np.zeros(num_records, dtype=int)
    vehicle_views = np.zeros(num_records, dtype=int)
    general_views = np.zeros(num_records, dtype=int)

    health_time = np.zeros(num_records, dtype=int)
    life_time = np.zeros(num_records, dtype=int)
    vehicle_time = np.zeros(num_records, dtype=int)
    general_time = np.zeros(num_records, dtype=int)

    total_sessions = np.zeros(num_records, dtype=int)
    return_visits = np.zeros(num_records, dtype=int)
    quote_requests = np.zeros(num_records, dtype=int)
    callback_requests = np.zeros(num_records, dtype=int)
    chat_count = np.zeros(num_records, dtype=int)
    doubts = np.zeros(num_records, dtype=int)
    questions = np.zeros(num_records, dtype=int)
    risk_score = np.zeros(num_records, dtype=int)
    prev_agent_failed = np.zeros(num_records, dtype=bool)
    intents = []
    messages = []

    for i in range(num_records):
        arch = archetypes[i]
        primary_domain = np.random.choice(DOMAINS, p=[0.40, 0.30, 0.20, 0.10])

        if arch == 0:  # Direct Willing Buyer (Low complexity, High willingness)
            selected_cat = primary_domain if random.random() < 0.85 else "None"
            pv = random.randint(3, 8)
            time_spent = pv * random.randint(35, 75)
            if primary_domain == "Health":
                health_views[i] = pv
                health_time[i] = time_spent
            elif primary_domain == "Life":
                life_views[i] = pv
                life_time[i] = time_spent
            elif primary_domain == "Vehicle":
                vehicle_views[i] = pv
                vehicle_time[i] = time_spent
            else:
                general_views[i] = pv
                general_time[i] = time_spent

            total_sessions[i] = random.randint(2, 5)
            return_visits[i] = total_sessions[i] - 1
            quote_requests[i] = random.randint(1, 3)
            callback_requests[i] = random.choice([1, 2])
            chat_count[i] = random.randint(0, 2)
            doubts[i] = 0
            questions[i] = random.randint(0, 1)
            risk_score[i] = random.randint(10, 30)
            prev_agent_failed[i] = False
            intent = "Ready to buy" if random.random() < 0.85 else "Interested"

        elif arch == 1:  # Multi-category Comparer (Medium complexity, Med/Low willingness)
            selected_cat = "None" if random.random() < 0.65 else random.choice(DOMAINS)
            health_views[i] = random.randint(2, 5)
            life_views[i] = random.randint(2, 5)
            vehicle_views[i] = random.choice([0, 1, 2])
            health_time[i] = health_views[i] * random.randint(20, 45)
            life_time[i] = life_views[i] * random.randint(20, 45)
            vehicle_time[i] = vehicle_views[i] * random.randint(15, 30)

            total_sessions[i] = random.randint(3, 6)
            return_visits[i] = random.randint(1, 3)
            quote_requests[i] = random.choice([0, 1])
            callback_requests[i] = random.choice([0, 1])
            chat_count[i] = random.randint(2, 5)
            doubts[i] = random.randint(2, 4)
            questions[i] = random.randint(3, 6)
            risk_score[i] = random.randint(25, 50)
            prev_agent_failed[i] = False
            intent = "Needs guidance" if random.random() < 0.70 else "Interested"

        elif arch == 2:  # Price / Trust Objection (Medium complexity, Low/Med willingness)
            selected_cat = primary_domain
            pv = random.randint(4, 9)
            time_spent = pv * random.randint(30, 60)
            if primary_domain == "Health":
                health_views[i] = pv
                health_time[i] = time_spent
            elif primary_domain == "Life":
                life_views[i] = pv
                life_time[i] = time_spent
            else:
                vehicle_views[i] = pv
                vehicle_time[i] = time_spent

            total_sessions[i] = random.randint(3, 7)
            return_visits[i] = random.randint(2, 4)
            quote_requests[i] = random.choice([0, 1])
            callback_requests[i] = 0
            chat_count[i] = random.randint(2, 4)
            doubts[i] = random.randint(3, 5)
            questions[i] = random.randint(2, 4)
            risk_score[i] = random.randint(35, 60)
            prev_agent_failed[i] = False
            intent = "Price objection" if random.random() < 0.60 else "Trust objection"

        elif arch == 3:  # High-Complexity Multi-domain (Senior Expert candidate)
            selected_cat = "None" if random.random() < 0.50 else primary_domain
            health_views[i] = random.randint(4, 8)
            life_views[i] = random.randint(4, 8)
            general_views[i] = random.randint(1, 4)
            health_time[i] = health_views[i] * random.randint(50, 90)
            life_time[i] = life_views[i] * random.randint(50, 90)
            general_time[i] = general_views[i] * random.randint(30, 60)

            total_sessions[i] = random.randint(6, 12)
            return_visits[i] = random.randint(4, 8)
            quote_requests[i] = random.randint(1, 4)
            callback_requests[i] = random.randint(1, 3)
            chat_count[i] = random.randint(5, 10)
            doubts[i] = random.randint(5, 8)
            questions[i] = random.randint(6, 10)
            risk_score[i] = random.randint(55, 85)
            prev_agent_failed[i] = False
            intent = random.choice(["Needs guidance", "Interested", "Price objection"])

        elif arch == 4:  # Previous Agent Failed / Escalation (Senior Expert override)
            selected_cat = primary_domain
            pv = random.randint(3, 6)
            time_spent = pv * random.randint(40, 70)
            if primary_domain == "Health":
                health_views[i] = pv
                health_time[i] = time_spent
            else:
                life_views[i] = pv
                life_time[i] = time_spent

            total_sessions[i] = random.randint(4, 8)
            return_visits[i] = random.randint(3, 6)
            quote_requests[i] = random.choice([1, 2])
            callback_requests[i] = 1
            chat_count[i] = random.randint(3, 6)
            doubts[i] = random.randint(2, 5)
            questions[i] = random.randint(2, 5)
            risk_score[i] = random.randint(40, 75)
            prev_agent_failed[i] = True
            intent = random.choice(["Trust objection", "Needs guidance", "Price objection"])

        else:  # Casual Browser (Low engagement, low willingness)
            selected_cat = "None" if random.random() < 0.70 else random.choice(DOMAINS)
            if random.random() < 0.5:
                health_views[i] = random.randint(1, 2)
                health_time[i] = health_views[i] * random.randint(15, 30)
            else:
                vehicle_views[i] = random.randint(1, 2)
                vehicle_time[i] = vehicle_views[i] * random.randint(15, 30)

            total_sessions[i] = random.choice([1, 2])
            return_visits[i] = total_sessions[i] - 1
            quote_requests[i] = 0
            callback_requests[i] = 0
            chat_count[i] = random.choice([0, 1])
            doubts[i] = random.choice([0, 1])
            questions[i] = random.choice([0, 1])
            risk_score[i] = random.randint(15, 35)
            prev_agent_failed[i] = False
            intent = random.choice(["General enquiry", "Unwilling", "No message"])

        selected_category.append(selected_cat)
        intents.append(intent)
        msg_template = random.choice(INTENT_TEMPLATES[intent])
        messages.append(msg_template)

    # Convert to DataFrame
    df = pd.DataFrame({
        "customer_id": [f"CUST{100000 + i}" for i in range(num_records)],
        "age": ages,
        "monthly_income": incomes,
        "credit_score": credit_scores,
        "marital_status": marital_status,
        "dependents": dependents,
        "existing_policy": existing_policy,
        "selected_category": selected_category,
        "health_page_views": health_views,
        "life_page_views": life_views,
        "vehicle_page_views": vehicle_views,
        "general_page_views": general_views,
        "health_time": health_time,
        "life_time": life_time,
        "vehicle_time": vehicle_time,
        "general_time": general_time,
        "total_sessions": total_sessions,
        "return_visits": return_visits,
        "quote_requests": quote_requests,
        "callback_requests": callback_requests,
        "chat_count": chat_count,
        "doubts": doubts,
        "questions": questions,
        "risk_score": risk_score,
        "previous_agent_failed": prev_agent_failed,
        "language": languages,
        "customer_message": messages,
        "conversation_intent": intents
    })

    # Ground-truth Target Labels Calculation (with realistic noise)
    # 1. Insurance Domain
    domain_scores = {
        "Health": df["health_page_views"] * 10 + df["health_time"] / 10 + (df["selected_category"] == "Health") * 80,
        "Life": df["life_page_views"] * 10 + df["life_time"] / 10 + (df["selected_category"] == "Life") * 80,
        "Vehicle": df["vehicle_page_views"] * 10 + df["vehicle_time"] / 10 + (df["selected_category"] == "Vehicle") * 80,
        "General": df["general_page_views"] * 10 + df["general_time"] / 10 + (df["selected_category"] == "General") * 80,
    }
    domain_matrix = pd.DataFrame(domain_scores)
    # If all 0, default to Health or General
    domain_target = domain_matrix.idxmax(axis=1)
    df["insurance_domain"] = domain_target

    # 2. Engagement Score & Level (0-100)
    # Using the weighted formula from Part 5:
    # Sessions: 15, Return visits: 20, Relevant views: 20, Relevant time: 15, Chat: 10, Quote: 10, Callback: 10
    total_views = df["health_page_views"] + df["life_page_views"] + df["vehicle_page_views"] + df["general_page_views"]
    total_time = df["health_time"] + df["life_time"] + df["vehicle_time"] + df["general_time"]

    eng_score = (
        np.clip(df["total_sessions"] / 6.0, 0, 1) * 15 +
        np.clip(df["return_visits"] / 4.0, 0, 1) * 20 +
        np.clip(total_views / 10.0, 0, 1) * 20 +
        np.clip(total_time / 400.0, 0, 1) * 15 +
        np.clip(df["chat_count"] / 4.0, 0, 1) * 10 +
        np.clip(df["quote_requests"] / 2.0, 0, 1) * 10 +
        np.clip(df["callback_requests"] / 2.0, 0, 1) * 10
    )
    # Add slight random noise to avoid deterministic overfitting
    eng_score = np.clip(eng_score + np.random.normal(0, 3, size=num_records), 0, 100)
    df["engagement_score"] = np.round(eng_score, 1)
    df["engagement_level"] = pd.cut(df["engagement_score"], bins=[-1, 30, 65, 101], labels=["Low", "Medium", "High"])

    # 3. Purchase Willingness Score & Level (0-100)
    # Quote: 30, Callback: 25, Intent factor: 25, Return visits: 10, Time: 10
    intent_weights = {
        "Ready to buy": 25,
        "Interested": 18,
        "Needs guidance": 10,
        "General enquiry": 6,
        "No message": 4,
        "Price objection": 2,
        "Trust objection": 1,
        "Unwilling": -15
    }
    intent_score = df["conversation_intent"].map(intent_weights).fillna(5)

    will_score = (
        np.clip(df["quote_requests"] / 2.0, 0, 1) * 30 +
        np.clip(df["callback_requests"] / 1.0, 0, 1) * 25 +
        intent_score +
        np.clip(df["return_visits"] / 3.0, 0, 1) * 10 +
        np.clip(total_time / 350.0, 0, 1) * 10
    )
    will_score = np.clip(will_score + np.random.normal(0, 3, size=num_records), 0, 100)
    df["willingness_score"] = np.round(will_score, 1)
    df["purchase_willingness"] = pd.cut(df["willingness_score"], bins=[-1, 30, 65, 101], labels=["Low", "Medium", "High"])

    # 4. Customer Complexity Score & Level (0-100)
    # Categories count: 20, Doubts: 25, Questions: 25, Previous agent failed: 20, Chat count: 10
    cats_viewed = (
        (df["health_page_views"] > 0).astype(int) +
        (df["life_page_views"] > 0).astype(int) +
        (df["vehicle_page_views"] > 0).astype(int) +
        (df["general_page_views"] > 0).astype(int)
    )

    comp_score = (
        np.clip((cats_viewed - 1) / 2.0, 0, 1) * 20 +
        np.clip(df["doubts"] / 5.0, 0, 1) * 25 +
        np.clip(df["questions"] / 6.0, 0, 1) * 25 +
        df["previous_agent_failed"].astype(int) * 20 +
        np.clip(df["chat_count"] / 6.0, 0, 1) * 10
    )
    comp_score = np.clip(comp_score + np.random.normal(0, 2, size=num_records), 0, 100)
    df["complexity_score"] = np.round(comp_score, 1)
    df["customer_complexity"] = pd.cut(df["complexity_score"], bins=[-1, 30, 65, 101], labels=["Low", "Medium", "High"])

    # 5. Required Agent Level
    # Combine according to Decision Matrix and Business Overrides:
    # Rule 1: previous_agent_failed == True -> Senior Expert
    # Rule 2: customer_complexity == 'High' -> Senior Expert
    # Rule 3: High willingness and Low complexity -> Intern
    # Rule 4: Otherwise -> Expert
    def determine_agent(row):
        if row["previous_agent_failed"]:
            return "Senior Expert Agent"
        if row["customer_complexity"] == "High":
            return "Senior Expert Agent"
        if row["purchase_willingness"] == "High" and row["customer_complexity"] == "Low":
            return "Intern Agent"
        return "Expert Agent"

    df["required_agent_level"] = df.apply(determine_agent, axis=1)

    # Inject controlled realistic missing values (~1.5%) in a few non-critical numeric columns
    # to evaluate and use SimpleImputer properly
    for col in ["monthly_income", "credit_score", "chat_count"]:
        mask = np.random.rand(num_records) < 0.015
        df.loc[mask, col] = np.nan

    # Save to CSV
    df.to_csv(CUSTOMERS_CSV, index=False)
    print(f"Saved {num_records} customer records to {CUSTOMERS_CSV}")

    # Generate Summary Report
    summary = {
        "dataset_type": "Synthetic Customer Routing Dataset (PolicyBuzar)",
        "total_rows": int(len(df)),
        "num_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "duplicate_records": int(df.duplicated(subset=["customer_id"]).sum()),
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns if df[col].isna().sum() > 0},
        "class_distributions": {
            "insurance_domain": df["insurance_domain"].value_counts().to_dict(),
            "engagement_level": df["engagement_level"].value_counts().to_dict(),
            "purchase_willingness": df["purchase_willingness"].value_counts().to_dict(),
            "customer_complexity": df["customer_complexity"].value_counts().to_dict(),
            "conversation_intent": df["conversation_intent"].value_counts().to_dict(),
            "required_agent_level": df["required_agent_level"].value_counts().to_dict(),
        }
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved summary report to {SUMMARY_JSON}")
    return df, summary


def generate_agents(num_agents=40):
    print(f"Generating {num_agents} synthetic agents with guaranteed domain and language coverage...")
    agent_names = [
        "Rahul Sharma", "Priya Patel", "Venkat Rao", "Lakshmi Devi", "Amit Verma",
        "Sneha Kulkarni", "Suresh Reddy", "Deepa Nair", "Arjun Sen", "Fatima Sheikh",
        "Kavita Joshi", "Rohan Mehta", "Ananya Das", "Manish Gupta", "Pooja Hegde",
        "Vikram Malhotra", "Swati Deshmukh", "Naveen Kumar", "Divya Menon", "Gaurav Bhatt",
        "Meera Krishnan", "Siddharth Roy", "Bhavna Mishra", "Harish Iyer", "Shreya Bannerjee",
        "Rajeshwari Rao", "Karthik Raja", "Sunita Agarwal", "Tarun Choudhary", "Gayatri Pillai",
        "Pradeep Nair", "Archana Singh", "Vijay Anand", "Pallavi Kulkarni", "Mohammad Aslam",
        "Geetha Reddy", "Ashok Pandey", "Neelam Saxena", "Balaji Natarajan", "Vandana Seth"
    ]

    agent_records = []
    # Levels distribution: 14 Interns, 16 Experts, 10 Senior Experts
    levels = (
        ["Intern Agent"] * 14 +
        ["Expert Agent"] * 16 +
        ["Senior Expert Agent"] * 10
    )

    target_domains = ["Health", "Life", "Vehicle", "General"]
    target_langs = ["Hindi", "Telugu", "Tamil", "Kannada", "Marathi", "Bengali", "Gujarati"]

    for i in range(num_agents):
        aid = f"AG{101 + i}"
        name = agent_names[i]
        lvl = levels[i]

        dom_primary = target_domains[i % 4]
        dom_secondary = target_domains[(i + 1) % 4]

        if lvl == "Intern Agent":
            exp = round(0.5 + (i % 4) * 0.4, 1)
            specs = [dom_primary]
            max_wl = 4
        elif lvl == "Expert Agent":
            exp = round(2.5 + (i % 6) * 0.5, 1)
            specs = [dom_primary, dom_secondary]
            max_wl = 5
        else:
            exp = round(5.5 + (i % 8) * 1.0, 1)
            specs = [dom_primary, dom_secondary, "General"]
            max_wl = 6

        lang1 = target_langs[i % len(target_langs)]
        lang2 = target_langs[(i + 3) % len(target_langs)]
        langs = ["English", lang1]
        if i % 3 == 0 and lang2 != lang1:
            langs.append(lang2)

        # Explicitly ensure Telugu Life Expert (e.g. AG119 or AG127)
        if aid == "AG127":
            specs = ["Life", "Health"]
            langs = ["English", "Telugu"]
            exp = 4.2
        if aid == "AG107":
            specs = ["Health", "Life"]
            langs = ["English", "Telugu"]

        is_online = True if i % 7 != 0 else False
        if not is_online:
            avail_status = "Offline"
            curr_wl = max_wl
        else:
            avail_status = "Available" if i % 5 != 0 else "In Call"
            curr_wl = (i % (max_wl - 1)) if avail_status == "Available" else max_wl

        assigned_custs = 20 + i * 5
        perf_rating = round(4.2 + (i % 8) * 0.1, 2)

        agent_records.append({
            "agent_id": aid,
            "agent_name": name,
            "agent_level": lvl,
            "specializations": ",".join(specs),
            "supported_languages": ",".join(langs),
            "experience_years": exp,
            "availability_status": avail_status,
            "is_online": is_online,
            "current_workload": curr_wl,
            "max_workload": max_wl,
            "assigned_customer_count": assigned_custs,
            "performance_rating": min(perf_rating, 4.95)
        })

    agents_df = pd.DataFrame(agent_records)
    agents_df.to_csv(AGENTS_CSV, index=False)
    print(f"Saved {num_agents} agents to {AGENTS_CSV}")
    return agents_df


if __name__ == "__main__":
    generate_customers(100000)
    generate_agents(40)
    print("Dataset generation completed successfully.")
