# Insurance Agent AI Frontend

React + Vite frontend for testing the Flask backend.

## Start backend first

From the backend project:

```bash
pip install -r requirements.txt
python src/train_tabular.py
python src/train_intent.py
python src/app.py
```

Backend should run at:

http://127.0.0.1:5000

## Start frontend

In this folder:

```bash
npm install
npm run dev
```

Open:

http://localhost:5173

## What this UI tests

- Health / Life / Vehicle / General behavior
- Customers who did not explicitly select a category
- Conversation intent
- Engagement
- Purchase intent
- Complexity
- LR + DT + RF + KNN voting output
- Agent assignment
- Senior/Expert routing for complex cases

The frontend sends the customer's data to:

POST http://127.0.0.1:5000/analyze
