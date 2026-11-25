"""
PolicyBuzar - Dual Storage Service (MongoDB + JSON Fallback)
Handles collections:
- customers
- predictions
- agents
- assignments (with complete customer interaction history & outcome tracking)
- feedback
Automatically connects to MongoDB if available, otherwise seamlessly persists
records to local JSON files in backend/database/storage/.
"""

import os
import json
import random
import datetime
import pandas as pd

DB_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(DB_DIR, "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

AGENTS_CSV = os.path.join(os.path.dirname(DB_DIR), "data", "synthetic_agents.csv")

# Try MongoDB connection with short timeout
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "policybuzar"


class StorageService:
    def __init__(self):
        self.is_mongo = False
        self.client = None
        self.db = None
        self._init_connection()
        self._seed_agents_if_empty()
        self._seed_assignments_if_empty()

    def _init_connection(self):
        try:
            import pymongo
            client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=800)
            client.server_info()
            self.client = client
            self.db = client[DB_NAME]
            self.is_mongo = True
            print("Connected to MongoDB successfully.")
        except Exception as e:
            self.is_mongo = False
            self.client = None
            self.db = None
            print(f"MongoDB unavailable ({e}). Using persistent JSON fallback storage.")

    def _get_json_file(self, collection_name):
        return os.path.join(STORAGE_DIR, f"{collection_name}.json")

    def _read_json(self, collection_name):
        fpath = self._get_json_file(collection_name)
        if not os.path.exists(fpath):
            return []
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, collection_name, data):
        fpath = self._get_json_file(collection_name)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _seed_agents_if_empty(self):
        agents = self.get_all_agents()
        if not agents and os.path.exists(AGENTS_CSV):
            df = pd.read_csv(AGENTS_CSV)
            agent_list = df.to_dict(orient="records")
            for a in agent_list:
                a["is_online"] = bool(a.get("is_online", True))
                if isinstance(a.get("specializations"), str):
                    a["specializations"] = [s.strip() for s in a["specializations"].split(",")]
                if isinstance(a.get("supported_languages"), str):
                    a["supported_languages"] = [s.strip() for s in a["supported_languages"].split(",")]

            if self.is_mongo:
                self.db.agents.insert_many(agent_list)
            else:
                self._write_json("agents", agent_list)
            print(f"Seeded {len(agent_list)} agents into database.")

    def _seed_assignments_if_empty(self):
        existing = self.get_all_assignments()
        if existing:
            return

        agents = self.get_all_agents()
        if not agents:
            return

        mock_customer_names = [
            "Amitabh Sen", "Rohit Verma", "Sunita Nair", "Kavita Rao", "Deepak Joshi",
            "Sanjay Gupta", "Pooja Hegde", "Arun Bhatt", "Meera Kulkarni", "Vikas Patel",
            "Ananya Roy", "Rajeshwari Iyer", "Naveen Choudhary", "Fatima Khan", "Manish Saxena"
        ]

        sample_cases = []
        base_date = datetime.date(2026, 11, 15)

        for i, agent in enumerate(agents):
            specs = agent.get("specializations", ["Health"])
            primary_dom = specs[0] if specs else "Health"
            level = agent.get("agent_level", "Intern Agent")

            # Create 3-4 historical cases per agent
            num_cases = 3 if level == "Intern Agent" else 4
            for c_idx in range(num_cases):
                cid = f"CASE-{agent['agent_id']}-{c_idx + 1}"
                cust_id = f"CUST100{i*10 + c_idx + 10}"
                cust_name = mock_customer_names[(i * 3 + c_idx) % len(mock_customer_names)]
                date_assigned = (base_date + datetime.timedelta(days=(c_idx * 2 + (i % 5)))).isoformat()

                # 1st case succeeded, 2nd in_progress or succeeded, 3rd can be tested as failed
                if c_idx == 0:
                    outcome = "succeeded"
                    notes = f"Successfully assisted with {primary_dom} policy selection and closed KYC."
                elif c_idx == 1:
                    outcome = "succeeded" if level != "Intern Agent" else "in_progress"
                    notes = f"Completed plan comparison for family {primary_dom} floater."
                else:
                    outcome = "in_progress"
                    notes = "Customer reviewing premium quotation and waiting for callback."

                comp_level = "Low" if level == "Intern Agent" else ("Medium" if level == "Expert Agent" else "High")

                sample_cases.append({
                    "case_id": cid,
                    "customer_id": cust_id,
                    "customer_name": cust_name,
                    "agent_id": agent["agent_id"],
                    "agent_name": agent["agent_name"],
                    "agent_level": level,
                    "domain": primary_dom,
                    "complexity": comp_level,
                    "date_assigned": date_assigned,
                    "outcome": outcome,
                    "outcome_notes": notes,
                    "escalated_to": None,
                    "escalated_to_name": None,
                    "escalated_to_level": None,
                    "customer_data": {
                        "age": 28 + (c_idx * 7 + i % 15),
                        "monthly_income": 45000 + (i * 2000),
                        "credit_score": 680 + (i * 3),
                        "marital_status": "Married" if c_idx > 0 else "Single",
                        "dependents": c_idx,
                        "existing_policy": False,
                        "selected_category": primary_dom,
                        "health_page_views": 4 if primary_dom == "Health" else 0,
                        "life_page_views": 4 if primary_dom == "Life" else 0,
                        "vehicle_page_views": 4 if primary_dom == "Vehicle" else 0,
                        "general_page_views": 4 if primary_dom == "General" else 0,
                        "health_time": 220 if primary_dom == "Health" else 0,
                        "life_time": 220 if primary_dom == "Life" else 0,
                        "vehicle_time": 220 if primary_dom == "Vehicle" else 0,
                        "general_time": 220 if primary_dom == "General" else 0,
                        "total_sessions": 3,
                        "return_visits": 2,
                        "quote_requests": 1,
                        "callback_requests": 1,
                        "chat_count": 2,
                        "doubts": 1 if level != "Senior Expert Agent" else 4,
                        "questions": 2 if level != "Senior Expert Agent" else 5,
                        "risk_score": 25,
                        "previous_agent_failed": False,
                        "language": "English",
                        "customer_message": f"Need assistance finalizing my {primary_dom} policy."
                    }
                })

        if self.is_mongo:
            self.db.assignments.insert_many(sample_cases)
        else:
            self._write_json("assignments", sample_cases)
        print(f"Seeded {len(sample_cases)} historical assignment cases across 40 agents.")

    def insert_record(self, collection_name, record):
        record_copy = dict(record)
        record_copy["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.is_mongo:
            res = self.db[collection_name].insert_one(record_copy)
            record_copy["_id"] = str(res.inserted_id)
            return record_copy
        else:
            records = self._read_json(collection_name)
            record_copy["_id"] = f"{collection_name}_{len(records) + 1}_{int(datetime.datetime.now().timestamp())}"
            records.append(record_copy)
            self._write_json(collection_name, records)
            return record_copy

    def get_all_agents(self):
        if self.is_mongo:
            agents = list(self.db.agents.find({}, {"_id": 0}))
            return agents
        else:
            return self._read_json("agents")

    def get_agent_by_id(self, agent_id):
        if self.is_mongo:
            return self.db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        else:
            agents = self._read_json("agents")
            for a in agents:
                if a.get("agent_id") == agent_id:
                    return a
            return None

    def update_agent(self, agent_id, updates):
        if self.is_mongo:
            self.db.agents.update_one({"agent_id": agent_id}, {"$set": updates})
        else:
            agents = self._read_json("agents")
            for a in agents:
                if a.get("agent_id") == agent_id:
                    a.update(updates)
                    break
            self._write_json("agents", agents)

    def get_all_assignments(self):
        if self.is_mongo:
            return list(self.db.assignments.find({}, {"_id": 0}))
        else:
            return self._read_json("assignments")

    def get_agent_history(self, agent_id):
        if self.is_mongo:
            return list(self.db.assignments.find({"agent_id": agent_id}, {"_id": 0}).sort("date_assigned", -1))
        else:
            cases = self._read_json("assignments")
            return [c for c in cases if c.get("agent_id") == agent_id]

    def update_case_outcome(self, agent_id, case_id, outcome, notes=""):
        if self.is_mongo:
            self.db.assignments.update_one(
                {"case_id": case_id},
                {"$set": {"outcome": outcome, "outcome_notes": notes, "updated_at": datetime.datetime.now().isoformat()}}
            )
            return self.db.assignments.find_one({"case_id": case_id}, {"_id": 0})
        else:
            cases = self._read_json("assignments")
            matched = None
            for c in cases:
                if c.get("case_id") == case_id:
                    c["outcome"] = outcome
                    if notes:
                        c["outcome_notes"] = notes
                    c["updated_at"] = datetime.datetime.now().isoformat()
                    matched = c
                    break
            self._write_json("assignments", cases)
            return matched

    def get_stats(self):
        if self.is_mongo:
            return {
                "engine": "MongoDB",
                "counts": {col: self.db[col].count_documents({}) for col in ["customers", "predictions", "agents", "assignments", "feedback"]}
            }
        else:
            return {
                "engine": "JSON Fallback Storage",
                "counts": {col: len(self._read_json(col)) for col in ["customers", "predictions", "agents", "assignments", "feedback"]}
            }


# Singleton instance
db_service = StorageService()
