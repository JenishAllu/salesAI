from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "customer_agent_routing_100k.csv"

REQUIRED_COLUMNS = {
    "age", "income_monthly", "credit_score", "marital_status",
    "dependents", "existing_policy", "selected_category", "domain",
    "engagement_level", "purchase_intent", "complexity_level", "agent_level",
}
DOMAINS = {"health", "life", "vehicle", "general"}
LEVELS = {"low", "medium", "high"}


def main():
    frame = pd.read_csv(DATA_FILE)
    missing_columns = REQUIRED_COLUMNS - set(frame.columns)
    assert not missing_columns, f"Missing columns: {sorted(missing_columns)}"
    assert len(frame) == 100_000, f"Expected 100000 rows, found {len(frame)}"
    assert not frame.isna().any().any(), "Dataset contains missing values"
    assert frame.age.between(18, 80).all(), "Age outside 18-80"
    assert frame.income_monthly.between(12_000, 900_000).all(), "Income outside expected range"
    assert frame.credit_score.between(300, 850).all(), "Credit score outside 300-850"
    assert frame.domain.isin(DOMAINS).all(), "Invalid domain label"
    for column in ["engagement_level", "purchase_intent", "complexity_level"]:
        assert frame[column].astype(str).str.lower().isin(LEVELS).all(), f"Invalid {column} label"
    assert frame.return_visits.le(frame.total_sessions - 1).all(), "Return visits exceed sessions"
    assert frame.selected_category.isin(DOMAINS | {"none"}).all(), "Invalid selected category"
    print(f"VALID: {len(frame):,} rows, {len(frame.columns)} columns, no missing values or invalid ranges")
    for column in ["domain", "engagement_level", "purchase_intent", "complexity_level"]:
        print(column, frame[column].value_counts(normalize=True).round(3).to_dict())


if __name__ == "__main__":
    main()
