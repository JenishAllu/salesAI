from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "customer_behavior_100k.csv"
RNG = np.random.default_rng(42)
N_ROWS = 100_000
DOMAINS = np.array(["health", "life", "vehicle", "general"])


def bounded_normal(mean, std, low, high, size):
    return np.clip(RNG.normal(mean, std, size), low, high).round().astype(int)


def label_from_score(score, low_threshold, high_threshold):
    return np.select(
        [score < low_threshold, score < high_threshold],
        ["low", "medium"],
        default="high",
    )


age = bounded_normal(44, 15, 18, 75, N_ROWS)
income_monthly = np.clip(
    RNG.lognormal(np.log(48_000), 0.58, N_ROWS), 12_000, 500_000
).round().astype(int)

# Credit is only weakly related to income and retains substantial independent noise.
income_rank = (income_monthly - income_monthly.mean()) / income_monthly.std()
credit_score = np.clip(
    680 + income_rank * 10 + RNG.normal(0, 62, N_ROWS), 300, 850
).round().astype(int)

marital_status = np.where(
    RNG.random(N_ROWS) < np.clip(0.35 + (age - 18) * 0.008, 0.35, 0.82),
    "married",
    "single",
)
dependents = np.clip(
    RNG.poisson(np.where(marital_status == "married", 1.7, 0.6)), 0, 5
).astype(int)

existing_policy = RNG.choice(
    ["none", "health", "life", "vehicle", "multiple"],
    N_ROWS,
    p=[0.52, 0.17, 0.13, 0.13, 0.05],
)
latent_domain = RNG.choice(DOMAINS, N_ROWS, p=[0.35, 0.25, 0.25, 0.15])
selected_category = np.where(
    RNG.random(N_ROWS) < 0.38,
    latent_domain,
    "none",
)

# Selected categories influence behavior but do not determine it, allowing inference.
domain_signal = np.zeros((N_ROWS, 4))
for index, domain in enumerate(DOMAINS):
    signal = (latent_domain == domain).astype(float)
    signal += (selected_category == domain) * 0.8
    signal += RNG.normal(0, 0.25, N_ROWS)
    domain_signal[:, index] = np.clip(signal, 0, None)

page_views = RNG.poisson(1.0 + domain_signal * 2.8).astype(int)
time_seconds = np.where(
    page_views > 0,
    RNG.gamma(2.2, 32, (N_ROWS, 4)) * (0.6 + page_views / 3),
    0,
).round().astype(int)
comparisons = RNG.binomial(
    page_views,
    np.clip(0.04 + domain_signal * 0.07, 0.02, 0.55),
).astype(int)

base_sessions = RNG.poisson(2.2, N_ROWS) + 1
total_sessions = np.clip(base_sessions + (page_views.sum(axis=1) / 8).round().astype(int), 1, 20)
return_visits = np.minimum(
    total_sessions - 1,
    RNG.poisson(np.clip(total_sessions * 0.45, 0.1, 8)),
).astype(int)
engagement_signal = (
    total_sessions * 0.8
    + return_visits * 0.9
    + page_views.sum(axis=1) * 0.2
    + time_seconds.sum(axis=1) / 180
)
quote_requests = RNG.poisson(np.clip(engagement_signal / 14, 0, 4)).astype(int)
callback_requests = RNG.binomial(
    np.minimum(quote_requests + 1, 2),
    np.clip(0.05 + engagement_signal / 100, 0.05, 0.35),
).astype(int)
chat_count = RNG.poisson(np.clip(engagement_signal / 16, 0, 7)).astype(int)

engagement_score = (
    total_sessions * 0.7
    + return_visits * 0.9
    + time_seconds.sum(axis=1) / 220
    + chat_count * 0.8
    + RNG.normal(0, 1.2, N_ROWS)
)
purchase_score = (
    quote_requests * 2.2
    + callback_requests * 2.5
    + comparisons.sum(axis=1) * 0.45
    + chat_count * 0.3
    + engagement_score * 0.2
    + RNG.normal(0, 1.4, N_ROWS)
)
complexity_score = (
    comparisons.sum(axis=1) * 0.9
    + dependents * 0.55
    + (existing_policy == "multiple") * 2.2
    + (existing_policy != "none") * 0.35
    + total_sessions * 0.25
    + chat_count * 0.35
    + callback_requests * 0.8
    + RNG.normal(0, 1.4, N_ROWS)
)

# Fixed business thresholds preserve meaningful class imbalance without quota labels.
engagement_level = label_from_score(engagement_score, 5.3, 7.8)
purchase_intent = label_from_score(purchase_score, 2.3, 4.45)
complexity_level = label_from_score(complexity_score, 2.8, 4.75)
primary_domain = DOMAINS[domain_signal.argmax(axis=1)]

frame = pd.DataFrame({
    "customer_id": [f"C{i:06d}" for i in range(1, N_ROWS + 1)],
    "age": age,
    "income_monthly": income_monthly,
    "credit_score": credit_score,
    "marital_status": marital_status,
    "dependents": dependents,
    "existing_policy": existing_policy,
    "selected_category": selected_category,
    "health_page_views": page_views[:, 0],
    "life_page_views": page_views[:, 1],
    "vehicle_page_views": page_views[:, 2],
    "general_page_views": page_views[:, 3],
    "health_time_seconds": time_seconds[:, 0],
    "life_time_seconds": time_seconds[:, 1],
    "vehicle_time_seconds": time_seconds[:, 2],
    "general_time_seconds": time_seconds[:, 3],
    "health_comparisons": comparisons[:, 0],
    "life_comparisons": comparisons[:, 1],
    "vehicle_comparisons": comparisons[:, 2],
    "general_comparisons": comparisons[:, 3],
    "total_sessions": total_sessions,
    "return_visits": return_visits,
    "quote_requests": quote_requests,
    "callback_requests": callback_requests,
    "chat_count": chat_count,
    "primary_domain": primary_domain,
    "engagement_level": engagement_level,
    "purchase_intent": purchase_intent,
    "complexity_level": complexity_level,
})

frame.to_csv(DATA_FILE, index=False)
print(f"Wrote {len(frame):,} rows to {DATA_FILE}")
print("Class distributions:")
for column in ["primary_domain", "engagement_level", "purchase_intent", "complexity_level"]:
    print(column, frame[column].value_counts(normalize=True).round(3).to_dict())
print("Credit score:", int(frame.credit_score.min()), int(frame.credit_score.max()), round(frame.credit_score.mean(), 1))
