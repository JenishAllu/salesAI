"""
PolicyBuzar - Dual Storage Service (MongoDB + JSON Fallback)
Handles collections:
- customers
- predictions
- agents
- assignments
- feedback
Automatically connects to MongoDB if available, otherwise seamlessly persists
records to local JSON files in backend/database/storage/.
"""

import os
import json
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
            # Convert boolean and lists
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

