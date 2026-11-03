
import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "customer_agent_routing_100k.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

FEATURES = [
    "age", "income_monthly", "income_lpa", "credit_score", "marital_status", "dependents", "existing_policy",
    "selected_category",
    "health_page_views", "life_page_views", "vehicle_page_views", "general_page_views",
    "health_time_seconds", "life_time_seconds", "vehicle_time_seconds", "general_time_seconds",
    "health_comparisons", "life_comparisons", "vehicle_comparisons", "general_comparisons",
    "total_sessions", "return_visits", "quote_requests", "callback_requests", "chat_count",
    "doubts_count", "questions_count", "risk_score", "previous_agent_failed"
]

CATEGORICAL = ["marital_status", "existing_policy", "selected_category"]
NUMERIC = [c for c in FEATURES if c not in CATEGORICAL]

X = df[FEATURES]

preprocessor = ColumnTransformer([
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), CATEGORICAL),
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ]), NUMERIC)
])

# The four algorithms from the original architecture:
# LR = Logistic Regression
# DT = Decision Tree
# RF = Random Forest
# KNN = K-Nearest Neighbors
def make_models():
    return [
        ("LR", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ("DT", DecisionTreeClassifier(
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42
        )),
        ("RF", RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            min_samples_leaf=2,
            n_jobs=-1,
            class_weight="balanced",
            random_state=42
        )),
        ("KNN", KNeighborsClassifier(
            n_neighbors=9,
            weights="distance",
            n_jobs=-1
        ))
    ]

def train_target(target, filename):
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    individual = {}
    fitted_models = {}

    # Train/evaluate each classifier separately.
    for name, estimator in make_models():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", estimator)
        ])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        acc = accuracy_score(y_test, pred)

        individual[name] = {
            "accuracy": float(acc),
            "classification_report": classification_report(
                y_test, pred, output_dict=True, zero_division=0
            ),
            "confusion_matrix": confusion_matrix(
                y_test, pred, labels=sorted(y.unique())
            ).tolist()
        }
        fitted_models[name] = pipe

        print(f"{target:20s} | {name:3s} | accuracy={acc:.4f}")

    # Majority/soft voting over the four classifiers.
    # All four use the same preprocessing, so the voting model is a pipeline.
    voting_estimators = [
        ("lr", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ("dt", DecisionTreeClassifier(
            max_depth=18, min_samples_leaf=2,
            class_weight="balanced", random_state=42
        )),
        ("rf", RandomForestClassifier(
            n_estimators=250, max_depth=18, min_samples_leaf=2,
            n_jobs=-1, class_weight="balanced", random_state=42
        )),
        ("knn", KNeighborsClassifier(
            n_neighbors=9, weights="distance", n_jobs=-1
        ))
    ]

    voting = Pipeline([
        ("preprocessor", preprocessor),
        ("voting", VotingClassifier(
            estimators=voting_estimators,
            voting="soft",
            n_jobs=-1
        ))
    ])

    voting.fit(X_train, y_train)
    voting_pred = voting.predict(X_test)
    voting_acc = accuracy_score(y_test, voting_pred)

    print(f"{target:20s} | VOTE | accuracy={voting_acc:.4f}")

    metrics = {
        "target": target,
        "individual_models": individual,
        "majority_vote": {
            "accuracy": float(voting_acc),
            "classification_report": classification_report(
                y_test, voting_pred, output_dict=True, zero_division=0
            ),
            "confusion_matrix": confusion_matrix(
                y_test, voting_pred, labels=sorted(y.unique())
            ).tolist()
        }
    }

    joblib.dump(voting, MODEL_DIR / filename)
    return metrics

targets = {
    "domain": "domain_voting_model.joblib",
    "engagement_level": "engagement_voting_model.joblib",
    "purchase_intent": "purchase_intent_voting_model.joblib",
    "complexity_level": "complexity_voting_model.joblib"
}

all_metrics = {}
for target, filename in targets.items():
    print("\n" + "=" * 80)
    print("TARGET:", target)
    all_metrics[target] = train_target(target, filename)

joblib.dump(FEATURES, MODEL_DIR / "features.joblib")

with open(MODEL_DIR / "training_metrics.json", "w") as f:
    json.dump(all_metrics, f, indent=2)

print("\nTraining complete.")
print("Four classifiers used: Logistic Regression, Decision Tree, Random Forest, KNN")
print("Final prediction: soft majority vote")
print("Saved models:", list(targets.values()))
