# 🛡️ PolicyBuzar — Complete Dynamic AI Customer Classification & Intelligent Agent Routing System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0.3-emerald.svg)](https://flask.palletsprojects.com/)
[![React 18](https://img.shields.io/badge/React-18.2-cyan.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5.2-orange.svg)](https://scikit-learn.org/)
[![MongoDB / Storage](https://img.shields.io/badge/Storage-MongoDB%20%7C%20JSON%20Fallback-green.svg)](https://www.mongodb.com/)
[![Test Suite](https://img.shields.io/badge/Acceptance%20Tests-14%2F14%20Passed-brightgreen.svg)]()

PolicyBuzar is an enterprise-grade AI customer classification and agent assignment platform inspired by Policybazaar. The system analyses customer profile data, browsing behaviors, and conversational intent to independently classify insurance needs and allocate the optimal qualified agent in real time.

---

## 📑 Table of Contents

1. [Core Business Architecture](#-core-business-architecture)
2. [5 Independent Prediction Outputs](#-5-independent-prediction-outputs)
3. [Machine Learning Architecture](#-machine-learning-architecture)
4. [Intelligent Agent Matching Engine](#-intelligent-agent-matching-engine)
5. [Decision Matrix & Escalation Policy](#-decision-matrix--escalation-policy)
6. [Synthetic Dataset (100,000 Records)](#-synthetic-dataset-100000-records)
7. [Frontend Live AI Simulator](#-frontend-live-ai-simulator)
8. [API Endpoints Reference](#-api-endpoints-reference)
9. [Automated Test Suite (14 Scenarios)](#-automated-test-suite-14-scenarios)
10. [Setup & Execution Instructions](#-setup--execution-instructions)

---

## 🏛️ Core Business Architecture

The primary objective of PolicyBuzar is:
> **Identify what the customer needs, understand their willingness to purchase, determine how difficult their requirements are, and assign the most appropriate available agent.**

```
                     +---------------------------------------+
                     |    Customer Form Inputs & Signals    |
                     +-------------------+-------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+-------------------+           +-------------------+           +-------------------+
|  1. Domain Model  |           | 2. Engagement Mod |           | 3. Willingness Mod|
| Health / Life /   |           | Low / Med / High  |           | Low / Med / High  |
| Vehicle / General |           | (Score 0-100)     |           | (TF-IDF NLP)      |
+---------+---------+           +---------+---------+           +---------+---------+
          |                               |                               |
          +-------------------------------+-------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     | 4. Customer Complexity Classification |
                     | Low / Medium / High (Score 0-100)     |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |  5. Central Policy Decision Matrix   |
                     |  - Escalation Overrides Check         |
                     |  - Intern / Expert / Senior Expert    |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+
                     | Intelligent Agent Matching Engine     |
                     | (Roster of 40 Agents: AG101 - AG140)  |
                     | Factors: Level, Domain, Language,     |
                     | Online, Capacity, Exp, Performance    |
                     +---------------------------------------+
```

---

## 🎯 5 Independent Prediction Outputs

Each customer interaction evaluates five independent classifications with its own output, confidence, reasoning, and relevant input features:

1. **Insurance Domain Prediction**:
   - Predicts: `Health`, `Life`, `Vehicle`, `General`, or `Unknown` (if insufficient evidence).
   - Rules: Explicit customer category selection is the strongest signal; otherwise inferred from browsing page views and dwell time. Supports multi-domain interest with secondary probabilities.
2. **Customer Engagement Classification**:
   - Predicts: `Low` (0–30), `Medium` (31–65), `High` (66–100).
   - Weighted Features: Sessions (15), Return visits (20), Relevant views (20), Time spent (15), Chat count (10), Quote requests (10), Callback requests (10).
   - *Condition*: High engagement does not automatically mean willingness to purchase.
3. **Purchase Willingness Classification**:
   - Predicts: `Low` (0–30), `Medium` (31–65), `High` (66–100).
   - Combines quote requests, callback requests, return visits, with an NLP classification of customer messages (8 intent classes: *Ready to buy, Interested, Needs guidance, Price objection, Trust objection, Unwilling, General enquiry, No message*).
4. **Customer Complexity Classification**:
   - Predicts: `Low` (0–30), `Medium` (31–65), `High` (66–100).
   - Driven by: single vs multiple insurance categories, recorded doubts, questions, chat interactions, unresolved issues, and previous agent failures.
   - *Anti-Bias Guarantee*: Age, income, and credit score do **not** automatically make a customer complex or escalate them.
5. **Final Agent Assignment**:
   - Determines: `Intern Agent`, `Expert Agent`, or `Senior Expert Agent`.
   - Dispatches the customer to a qualified, available agent from the 40-agent roster matching domain, language, workload capacity, and experience.

---

## 🧠 Machine Learning Architecture

For each target, PolicyBuzar implements 4 core ML algorithms plus a Soft-Voting Ensemble:
- **Logistic Regression (LR)**
- **Decision Tree (DT)**
- **Random Forest (RF)**
- **K-Nearest Neighbors (KNN)**
- **Soft-Voting Ensemble**

### Model Performance Metrics (Evaluated on Synthetic Test Split)

| ML Task | LR Accuracy | DT Accuracy | RF Accuracy | KNN Accuracy | Ensemble Accuracy |
|---|:---:|:---:|:---:|:---:|:---:|
| **Insurance Domain** | 94.4% | 95.0% | 95.5% | 94.7% | **95.6%** |
| **Customer Engagement** | 92.1% | 89.4% | 91.8% | 90.5% | **92.7%** |
| **Purchase Willingness** | 95.2% | 94.1% | 95.8% | 93.9% | **96.4%** |
| **Customer Complexity** | 96.5% | 95.8% | 97.0% | 95.3% | **97.2%** |
| **Conversation Intent (NLP)** | 100.0% | 77.3% | 91.2% | 98.8% | **98.8%** |

---

## 🤝 Intelligent Agent Matching Engine

PolicyBuzar maintains a synthetic database of 40 agents (`AG101` – `AG140`) across 3 tiers:
- **14 Intern Agents** (0.5 – 2.0 years experience, max capacity 4)
- **16 Expert Agents** (2.5 – 5.0 years experience, max capacity 5)
- **10 Senior Expert Agents** (5.5 – 14.0 years experience, max capacity 6)

### Matching Criteria:
1. **Tier Match**: Mandatory. Required agent tier is never downgraded silently.
2. **Online & Available**: Agent must be `is_online = True` and `availability_status = 'Available'`.
3. **Domain Specialization**: Agent's specializations must include the predicted insurance domain.
4. **Language Matching**: Supports English, Hindi, Telugu, Tamil, Kannada, Marathi, Bengali, Gujarati. Regional language preferences receive top priority.
5. **Workload Capacity**: Prioritizes qualified agents with lower `current_workload / max_workload`.
6. **Experience & Rating**: Uses historical customer resolution rating (4.2 – 4.95).

---

## 📋 Decision Matrix & Escalation Policy

Implemented in `backend/config/policy_config.py`:

| Purchase Willingness | Customer Complexity | Agent Tier |
|---|---|---|
| **High** | **Low** | **Intern Agent** |
| **High** | **Medium** | **Expert Agent** |
| **High** | **High** | **Senior Expert Agent** |
| **Medium** | **Low** | **Expert Agent** |
| **Medium** | **Medium** | **Expert Agent** |
| **Medium** | **High** | **Senior Expert Agent** |
| **Low** | **Low** | **Expert Agent** |
| **Low** | **Medium** | **Expert Agent** |
| **Low** | **High** | **Senior Expert Agent** |

### Escalation Overrides:
- `previous_agent_failed == True` $\rightarrow$ **Senior Expert Agent** (Immediate escalation).
- `customer_complexity == 'High'` $\rightarrow$ **Senior Expert Agent**.
- `high_willingness == True` and `complexity == 'High'` $\rightarrow$ **Senior Expert Agent** (Never routed to Intern).

---

## 📊 Synthetic Dataset (100,000 Records)

Generated via `backend/data/generate_dataset.py` with reproducible random seed `42`:
- **File**: `backend/data/synthetic_customers.csv` (100,000 rows, 36 columns, 0 duplicates).
- **Roster**: `backend/data/synthetic_agents.csv` (40 agents with unique IDs `AG101`–`AG140`).
- **Missing Values**: Realistic 1.5% non-critical missing values handled through `SimpleImputer`.
- **Summary**: `backend/data/dataset_summary.json`.

---

## 💻 Frontend Live AI Simulator

Built with React 18, Vite, and responsive styling:
- **Controlled State & Debouncing**: Live dynamic updates as inputs change (30ms for dropdowns/toggles, 250ms for typing).
- **Sequence Protection**: Uses `AbortController` and request IDs to prevent stale API responses from overwriting newer predictions.
- **10 Quick Demonstration Scenarios**:
  1. Ready-to-buy Health customer $\rightarrow$ Intern Agent
  2. Ready-to-buy Life customer $\rightarrow$ Intern Agent
  3. Vehicle customer $\rightarrow$ Intern Agent
  4. Multi-category confused customer $\rightarrow$ Expert Agent
  5. Price objection $\rightarrow$ Expert Agent
  6. Complex customer $\rightarrow$ Senior Expert Agent
  7. Previous agent failed $\rightarrow$ Senior Expert Agent
  8. High engagement but low willingness $\rightarrow$ Expert Agent
  9. High willingness + high complexity $\rightarrow$ Senior Expert Agent
  10. Language-specific matching (Telugu) $\rightarrow$ Telugu-speaking Expert
- **Sensitivity Panel ("Why did the assignment change?")**:
  Explains field modified, previous vs new value, predictions affected, and decision boundary crossed.
- **Multi-Model Confidence (Card 6)**:
  Compares LR, DT, RF, KNN, and Ensemble outputs side-by-side.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict` | Computes all 5 classifications & agent assignment with sensitivity analysis |
| `POST` | `/api/train` | Retrains models on synthetic dataset |
| `GET` | `/api/model-metrics` | Returns accuracy, F1, precision, recall for LR, DT, RF, KNN, Ensemble |
| `GET` | `/api/dataset/summary` | Returns 100,000 synthetic dataset statistics & class distributions |
| `GET` | `/api/agents` | Returns all 40 agents, availability, workloads, and ratings |
| `GET` | `/api/scenarios` | Returns the 10 predefined demo scenarios |
| `GET` | `/api/health` | Health check and engine status |
| `POST` | `/api/feedback` | Records customer and agent feedback outcomes |

---

## 🧪 Automated Test Suite (14 Scenarios)

Run the acceptance tests verifying all 14 scenarios from PART 20:

```bash
python -m unittest backend/tests/test_acceptance.py
```

### Test Coverage:
- `test_01_simple_willing_customer` $\rightarrow$ Intern Agent
- `test_02_multi_category_confused_customer` $\rightarrow$ Expert Agent
- `test_03_price_objection_customer` $\rightarrow$ Expert Agent
- `test_04_previous_agent_failed_escalation` $\rightarrow$ Senior Expert Agent
- `test_05_complex_multi_category_customer` $\rightarrow$ Senior Expert Agent
- `test_06_high_willingness_high_complexity` $\rightarrow$ Senior Expert Agent
- `test_07_high_engagement_low_willingness` $\rightarrow$ Expert Agent
- `test_08_language_matching_telugu` $\rightarrow$ Telugu-speaking agent
- `test_09_specialization_matching_life` $\rightarrow$ Life-specialized agent
- `test_10_agent_offline_handling` $\rightarrow$ Verified online/available agent assigned
- `test_11_workload_capacity_preference` $\rightarrow$ Agent workload capacity verified
- `test_12_missing_data_robustness` $\rightarrow$ SimpleImputer missing value handling
- `test_13_live_field_sensitivity_tracking` $\rightarrow$ Sensitivity analysis validation
- `test_14_reset_to_default` $\rightarrow$ Default customer state recovery

---

## 🚀 Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (Node v24 supported)
- (Optional) MongoDB running locally on port 27017 (PolicyBuzar automatically falls back to persistent JSON storage if MongoDB is offline)

### Step 1: Install Dependencies

```bash
# Python dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Generate Synthetic Dataset (if not already generated)

```bash
python backend/data/generate_dataset.py
```

### Step 3: Train ML Models (LR, DT, RF, KNN, Ensemble)

```bash
python backend/models/train.py
```

### Step 4: Run Acceptance Tests

```bash
python -m unittest backend/tests/test_acceptance.py
```

### Step 5: Launch the Application

#### Option A: Full-Stack Single Process (Recommended)
```bash
python run_app.py
```
Open your browser at `http://127.0.0.1:5000`.

#### Option B: Independent Dev Servers
Terminal 1 (Backend API):
```bash
python -m backend.app
```
Terminal 2 (React Vite Dev Server):
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000`.

