
# Insurance Agent AI Backend

## Architecture

The backend uses the four classifiers from the project architecture:

1. Logistic Regression (LR)
2. Decision Tree (DT)
3. Random Forest (RF)
4. K-Nearest Neighbors (KNN)

For each tabular prediction task, all four classifiers are trained and evaluated.

The final prediction is produced by a **soft voting / majority-vote ensemble**.

The four tabular prediction tasks are:

- Primary insurance domain: Health / Life / Vehicle / General
- Engagement: Low / Medium / High
- Purchase intent: Low / Medium / High
- Customer complexity: Low / Medium / High

There is also a separate TF-IDF + Logistic Regression NLP model for conversation intent.

## Flow

Customer data
    ↓
Preprocessing
    ↓
LR + DT + RF + KNN
    ↓
Voting Aggregator
    ↓
Domain / Engagement / Purchase Intent / Complexity
    ↓
Agent Router
    ↓
Intent Agent / Experienced Agent / Expert Agent / Senior Agent

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Train

Run from the project root:

```bash
python src/validate_dataset.py
python src/train_tabular.py
python src/train_intent.py
```

Training uses `data/customer_agent_routing_100k.csv` as the canonical updated dataset. `validate_dataset.py` checks row count, required fields, ranges, labels, missing values, and session consistency before training. The dataset is synthetic development data and does not represent real Policybazaar data.

The tabular training script prints accuracy and classification reports for:

```text
LR
DT
RF
KNN
VOTE
```

for every target.

Saved models:

```text
models/domain_voting_model.joblib
models/engagement_voting_model.joblib
models/purchase_intent_voting_model.joblib
models/complexity_voting_model.joblib
models/intent_model.joblib
models/features.joblib
models/training_metrics.json
```

## Start API

```bash
python src/app.py
```

## Test API

```bash
pip install requests
python src/test_api.py
```

## Important

The 100,000-customer dataset is synthetic development data. It is not Policybazaar's real customer data.

The production version should use customer events obtained through authorized access and appropriate privacy/consent controls.

The development dataset now includes `credit_score` on the standard 300-850 scale. These values are synthetic development values; replace them with authorized bureau or customer-provided scores and appropriate consent controls before production use.
