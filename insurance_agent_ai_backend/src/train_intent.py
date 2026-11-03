
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
MODEL_DIR.mkdir(exist_ok=True)

routing_data = DATA_DIR / "customer_agent_routing_100k.csv"
if routing_data.exists():
    source = pd.read_csv(routing_data, usecols=["customer_message", "intent"])
    intent_df = (
        source.rename(columns={"customer_message": "text"})
        .dropna()
        .assign(intent=lambda frame: frame["intent"].astype(str).str.lower())
        .query("text != ''")
        .drop_duplicates()
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )
else:
    intent_df = None

templates = {
    "purchase": [
        "I want to buy {domain} insurance",
        "I want to take a {domain} policy",
        "I am ready to purchase {domain} insurance",
        "How can I buy a {domain} policy",
        "I want to get insured for {domain}",
        "I would like to purchase insurance",
    ],
    "comparison": [
        "Which {domain} policy is better",
        "Compare {domain} insurance plans",
        "I want to compare policies",
        "Show me different {domain} plans",
        "Which plan should I choose",
        "I want to compare premiums",
    ],
    "information": [
        "Tell me about {domain} insurance",
        "What does this policy cover",
        "I need information about insurance",
        "Explain the coverage",
        "What are the benefits of this policy",
        "I have a question about insurance",
    ],
    "quote": [
        "How much is the premium",
        "Give me an insurance quote",
        "I want to calculate my premium",
        "How much will this policy cost",
        "Can I get a quote",
        "Show the premium for this plan",
    ],
    "renewal": [
        "I want to renew my policy",
        "My insurance is expiring",
        "How do I renew my insurance",
        "I need policy renewal",
        "My policy expires soon",
    ],
    "claim": [
        "I want to make an insurance claim",
        "How do I file a claim",
        "I have a claim question",
        "My claim is pending",
        "I need help with my claim",
    ],
    "not_interested": [
        "I don't want insurance",
        "I am not interested",
        "I don't want to buy a policy",
        "No, I don't need insurance",
        "I am not planning to purchase",
    ],
    "agent_request": [
        "I want to speak to an agent",
        "Please call me",
        "Connect me with an insurance agent",
        "I need to talk to someone",
        "Can an agent contact me",
    ],
}

domains = ["health", "life", "vehicle", "general"]
rows = []
for intent, texts in templates.items():
    for text in texts:
        for domain in domains:
            for _ in range(60):
                rows.append((text.format(domain=domain), intent))

# Add behavior-free/general utterances
extra = {
    "purchase": ["I am interested in getting insurance", "I want a policy"],
    "information": ["I want to know more", "Can you explain this"],
    "quote": ["What is the price", "Show me the cost"],
    "agent_request": ["Connect me to a person", "I need customer support"],
}
for intent, texts in extra.items():
    for t in texts:
        for _ in range(150):
            rows.append((t, intent))

if intent_df is None:
    intent_df = (
        pd.DataFrame(rows, columns=["text", "intent"])
        .drop_duplicates()
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )
intent_df.to_csv(DATA_DIR / "intent_dataset.csv", index=False)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )),
    ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))
])

label_counts = intent_df["intent"].value_counts()
if label_counts.min() < 2:
    print("Intent evaluation unavailable: some updated-dataset labels have fewer than two unique messages.")
    print("Label counts:", label_counts.to_dict())
else:
    X_train, X_test, y_train, y_test = train_test_split(
        intent_df["text"], intent_df["intent"],
        test_size=0.2, random_state=42, stratify=intent_df["intent"]
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print("Intent accuracy:", round(accuracy_score(y_test, pred), 4))
    print(classification_report(y_test, pred))

# Train the deployed model on every available labeled message.
model.fit(intent_df["text"], intent_df["intent"])
joblib.dump(model, MODEL_DIR / "intent_model.joblib")
print("Saved:", MODEL_DIR / "intent_model.joblib")
