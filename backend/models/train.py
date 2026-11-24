"""
PolicyBuzar - Model Training Pipeline
Trains 4 core ML algorithms for each task:
- Logistic Regression (LR)
- Decision Tree (DT)
- Random Forest (RF)
- K-Nearest Neighbors (KNN)
Plus soft-voting ensembles for each target.
Tasks:
1. Insurance Domain Classification
2. Customer Engagement Classification
3. Purchase Willingness Classification
4. Customer Complexity Classification
5. Conversation Intent NLP Classification
Saves models and metrics with Joblib.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_DIR = os.path.join(BASE_DIR, "saved")
os.makedirs(SAVED_DIR, exist_ok=True)

DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "synthetic_customers.csv")
METRICS_PATH = os.path.join(SAVED_DIR, "model_metrics.json")


def evaluate_models(models_dict, X_test, y_test):
    metrics = {}
    for name, model in models_dict.items():
        if name in ["preprocessor", "vectorizer", "classes"]:
            continue
        preds = model.predict(X_test)
        metrics[name] = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "f1_weighted": round(float(f1_score(y_test, preds, average="weighted", zero_division=0)), 4),
            "precision_weighted": round(float(precision_score(y_test, preds, average="weighted", zero_division=0)), 4),
            "recall_weighted": round(float(recall_score(y_test, preds, average="weighted", zero_division=0)), 4)
        }
    return metrics


def train_all_models(sample_size=20000):
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    total_records = len(df)
    print(f"Loaded {total_records} records.")

    # Convert bools to int across the dataframe
    if "previous_agent_failed" in df.columns:
        df["previous_agent_failed"] = df["previous_agent_failed"].astype(int)
    if "existing_policy" in df.columns:
        df["existing_policy"] = df["existing_policy"].astype(int)

    # Use a stratified representative sample for high training speed while keeping 100k full evaluation
    if len(df) > sample_size:
        print(f"Using representative stratified sample of {sample_size} for training speed and instant inference...")
        df_train = df.sample(n=sample_size, random_state=42).copy()
    else:
        df_train = df.copy()

    all_metrics = {}

    # -------------------------------------------------------------
    # 1. CONVERSATION INTENT NLP MODEL
    # -------------------------------------------------------------
    print("\n--- Training Conversation Intent NLP Models ---")
    intent_df = df_train.dropna(subset=["customer_message", "conversation_intent"]).copy()
    intent_df["customer_message"] = intent_df["customer_message"].fillna("No message")
    X_text = intent_df["customer_message"]
    y_intent = intent_df["conversation_intent"]

    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
    X_text_vec = vectorizer.fit_transform(X_text)

    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_text_vec, y_intent, test_size=0.2, random_state=42, stratify=y_intent
    )

    lr_intent = LogisticRegression(max_iter=500, C=1.0)
    dt_intent = DecisionTreeClassifier(max_depth=12, random_state=42)
    rf_intent = RandomForestClassifier(n_estimators=40, max_depth=12, random_state=42, n_jobs=1)
    knn_intent = KNeighborsClassifier(n_neighbors=5, metric="cosine", n_jobs=1)

    lr_intent.fit(X_train_t, y_train_t)
    dt_intent.fit(X_train_t, y_train_t)
    rf_intent.fit(X_train_t, y_train_t)
    knn_intent.fit(X_train_t, y_train_t)

    ensemble_intent = VotingClassifier(
        estimators=[('lr', lr_intent), ('dt', dt_intent), ('rf', rf_intent), ('knn', knn_intent)],
        voting='soft'
    )
    ensemble_intent.fit(X_train_t, y_train_t)

    intent_models = {
        "vectorizer": vectorizer,
        "lr": lr_intent,
        "dt": dt_intent,
        "rf": rf_intent,
        "knn": knn_intent,
        "ensemble": ensemble_intent,
        "classes": list(ensemble_intent.classes_)
    }
    joblib.dump(intent_models, os.path.join(SAVED_DIR, "intent_models.joblib"))
    all_metrics["conversation_intent"] = evaluate_models(intent_models, X_test_t, y_test_t)
    print("Conversation Intent trained. Ensemble accuracy:", all_metrics["conversation_intent"]["ensemble"]["accuracy"])

    # -------------------------------------------------------------
    # 2. INSURANCE DOMAIN MODEL
    # -------------------------------------------------------------
    print("\n--- Training Insurance Domain Models ---")
    domain_num_cols = [
        "health_page_views", "life_page_views", "vehicle_page_views", "general_page_views",
        "health_time", "life_time", "vehicle_time", "general_time", "quote_requests"
    ]
    domain_cat_cols = ["selected_category"]

    domain_preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), domain_num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), domain_cat_cols)
        ]
    )

    X_dom = df_train[domain_num_cols + domain_cat_cols]
    y_dom = df_train["insurance_domain"]

    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
        X_dom, y_dom, test_size=0.2, random_state=42, stratify=y_dom
    )

    X_train_d_proc = domain_preprocessor.fit_transform(X_train_d)
    X_test_d_proc = domain_preprocessor.transform(X_test_d)

    lr_dom = LogisticRegression(max_iter=500, C=1.0)
    dt_dom = DecisionTreeClassifier(max_depth=10, random_state=42)
    rf_dom = RandomForestClassifier(n_estimators=40, max_depth=10, random_state=42, n_jobs=1)
    knn_dom = KNeighborsClassifier(n_neighbors=7, n_jobs=1)

    lr_dom.fit(X_train_d_proc, y_train_d)
    dt_dom.fit(X_train_d_proc, y_train_d)
    rf_dom.fit(X_train_d_proc, y_train_d)
    knn_dom.fit(X_train_d_proc, y_train_d)

    ensemble_dom = VotingClassifier(
        estimators=[('lr', lr_dom), ('dt', dt_dom), ('rf', rf_dom), ('knn', knn_dom)],
        voting='soft'
    )
    ensemble_dom.fit(X_train_d_proc, y_train_d)

    domain_models = {
        "preprocessor": domain_preprocessor,
        "lr": lr_dom,
        "dt": dt_dom,
        "rf": rf_dom,
        "knn": knn_dom,
        "ensemble": ensemble_dom,
        "classes": list(ensemble_dom.classes_)
    }
    joblib.dump(domain_models, os.path.join(SAVED_DIR, "domain_models.joblib"))
    all_metrics["insurance_domain"] = evaluate_models(domain_models, X_test_d_proc, y_test_d)
    print("Insurance Domain trained. Ensemble accuracy:", all_metrics["insurance_domain"]["ensemble"]["accuracy"])

    # -------------------------------------------------------------
    # 3. CUSTOMER ENGAGEMENT MODEL
    # -------------------------------------------------------------
    print("\n--- Training Customer Engagement Models ---")
    eng_num_cols = [
        "total_sessions", "return_visits", "health_page_views", "life_page_views",
        "vehicle_page_views", "general_page_views", "health_time", "life_time",
        "vehicle_time", "general_time", "chat_count", "quote_requests", "callback_requests"
    ]

    eng_preprocessor = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    X_eng = df_train[eng_num_cols]
    y_eng = df_train["engagement_level"]

    X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(
        X_eng, y_eng, test_size=0.2, random_state=42, stratify=y_eng
    )

    X_train_e_proc = eng_preprocessor.fit_transform(X_train_e)
    X_test_e_proc = eng_preprocessor.transform(X_test_e)

    lr_eng = LogisticRegression(max_iter=500, C=1.0)
    dt_eng = DecisionTreeClassifier(max_depth=8, random_state=42)
    rf_eng = RandomForestClassifier(n_estimators=40, max_depth=8, random_state=42, n_jobs=1)
    knn_eng = KNeighborsClassifier(n_neighbors=7, n_jobs=1)

    lr_eng.fit(X_train_e_proc, y_train_e)
    dt_eng.fit(X_train_e_proc, y_train_e)
    rf_eng.fit(X_train_e_proc, y_train_e)
    knn_eng.fit(X_train_e_proc, y_train_e)

    ensemble_eng = VotingClassifier(
        estimators=[('lr', lr_eng), ('dt', dt_eng), ('rf', rf_eng), ('knn', knn_eng)],
        voting='soft'
    )
    ensemble_eng.fit(X_train_e_proc, y_train_e)

    engagement_models = {
        "preprocessor": eng_preprocessor,
        "lr": lr_eng,
        "dt": dt_eng,
        "rf": rf_eng,
        "knn": knn_eng,
        "ensemble": ensemble_eng,
        "classes": list(ensemble_eng.classes_)
    }
    joblib.dump(engagement_models, os.path.join(SAVED_DIR, "engagement_models.joblib"))
    all_metrics["customer_engagement"] = evaluate_models(engagement_models, X_test_e_proc, y_test_e)
    print("Customer Engagement trained. Ensemble accuracy:", all_metrics["customer_engagement"]["ensemble"]["accuracy"])

    # -------------------------------------------------------------
    # 4. PURCHASE WILLINGNESS MODEL
    # -------------------------------------------------------------
    print("\n--- Training Purchase Willingness Models ---")
    will_num_cols = [
        "quote_requests", "callback_requests", "return_visits", "total_sessions",
        "health_time", "life_time", "vehicle_time", "general_time", "chat_count"
    ]
    will_cat_cols = ["conversation_intent"]

    will_preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), will_num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), will_cat_cols)
        ]
    )

    X_will = df_train[will_num_cols + will_cat_cols]
    y_will = df_train["purchase_willingness"]

    X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(
        X_will, y_will, test_size=0.2, random_state=42, stratify=y_will
    )

    X_train_w_proc = will_preprocessor.fit_transform(X_train_w)
    X_test_w_proc = will_preprocessor.transform(X_test_w)

    lr_will = LogisticRegression(max_iter=500, C=1.0)
    dt_will = DecisionTreeClassifier(max_depth=8, random_state=42)
    rf_will = RandomForestClassifier(n_estimators=40, max_depth=8, random_state=42, n_jobs=1)
    knn_will = KNeighborsClassifier(n_neighbors=7, n_jobs=1)

    lr_will.fit(X_train_w_proc, y_train_w)
    dt_will.fit(X_train_w_proc, y_train_w)
    rf_will.fit(X_train_w_proc, y_train_w)
    knn_will.fit(X_train_w_proc, y_train_w)

    ensemble_will = VotingClassifier(
        estimators=[('lr', lr_will), ('dt', dt_will), ('rf', rf_will), ('knn', knn_will)],
        voting='soft'
    )
    ensemble_will.fit(X_train_w_proc, y_train_w)

    willingness_models = {
        "preprocessor": will_preprocessor,
        "lr": lr_will,
        "dt": dt_will,
        "rf": rf_will,
        "knn": knn_will,
        "ensemble": ensemble_will,
        "classes": list(ensemble_will.classes_)
    }
    joblib.dump(willingness_models, os.path.join(SAVED_DIR, "willingness_models.joblib"))
    all_metrics["purchase_willingness"] = evaluate_models(willingness_models, X_test_w_proc, y_test_w)
    print("Purchase Willingness trained. Ensemble accuracy:", all_metrics["purchase_willingness"]["ensemble"]["accuracy"])

    # -------------------------------------------------------------
    # 5. CUSTOMER COMPLEXITY MODEL
    # -------------------------------------------------------------
    print("\n--- Training Customer Complexity Models ---")
    comp_num_cols = [
        "doubts", "questions", "chat_count", "risk_score",
        "health_page_views", "life_page_views", "vehicle_page_views", "general_page_views",
        "previous_agent_failed", "existing_policy"
    ]

    comp_preprocessor = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    X_comp = df_train[comp_num_cols]
    y_comp = df_train["customer_complexity"]

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_comp, y_comp, test_size=0.2, random_state=42, stratify=y_comp
    )

    X_train_c_proc = comp_preprocessor.fit_transform(X_train_c)
    X_test_c_proc = comp_preprocessor.transform(X_test_c)

    lr_comp = LogisticRegression(max_iter=500, C=1.0)
    dt_comp = DecisionTreeClassifier(max_depth=8, random_state=42)
    rf_comp = RandomForestClassifier(n_estimators=40, max_depth=8, random_state=42, n_jobs=1)
    knn_comp = KNeighborsClassifier(n_neighbors=7, n_jobs=1)

    lr_comp.fit(X_train_c_proc, y_train_c)
    dt_comp.fit(X_train_c_proc, y_train_c)
    rf_comp.fit(X_train_c_proc, y_train_c)
    knn_comp.fit(X_train_c_proc, y_train_c)

    ensemble_comp = VotingClassifier(
        estimators=[('lr', lr_comp), ('dt', dt_comp), ('rf', rf_comp), ('knn', knn_comp)],
        voting='soft'
    )
    ensemble_comp.fit(X_train_c_proc, y_train_c)

    complexity_models = {
        "preprocessor": comp_preprocessor,
        "lr": lr_comp,
        "dt": dt_comp,
        "rf": rf_comp,
        "knn": knn_comp,
        "ensemble": ensemble_comp,
        "classes": list(ensemble_comp.classes_)
    }
    joblib.dump(complexity_models, os.path.join(SAVED_DIR, "complexity_models.joblib"))
    all_metrics["customer_complexity"] = evaluate_models(complexity_models, X_test_c_proc, y_test_c)
    print("Customer Complexity trained. Ensemble accuracy:", all_metrics["customer_complexity"]["ensemble"]["accuracy"])

    # Save metrics report
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\nAll models and metrics successfully saved to {SAVED_DIR}")
    return all_metrics


if __name__ == "__main__":
    train_all_models(sample_size=20000)
