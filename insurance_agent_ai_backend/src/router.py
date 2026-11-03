
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_FILE = ROOT / "data" / "agents.csv"

class AgentRouter:
    def __init__(self):
        self.agents = pd.read_csv(AGENTS_FILE)
        self.agents["availability"] = self.agents["availability"].astype(str).str.lower().eq("true")
        self.agents["domains_set"] = self.agents["domains"].fillna("").apply(lambda x: set(x.split("|")))
        self.agents["languages_set"] = self.agents["languages"].fillna("").apply(lambda x: set(x.split("|")))

    def required_role(self, analysis):
        complexity = analysis["complexity"]
        intent = analysis.get("intent")
        purchase_intent = analysis.get("purchase_intent")
        comparison_count = analysis.get("comparison_count")
        existing_policy = analysis.get("existing_policy", "none")
        senior_request = analysis.get("senior_request", False)

        if senior_request:
            return ["Senior Agent", "Expert Agent"]

        if intent == "not_interested":
            return ["Intent Agent", "Experienced Agent"]

        if complexity == "high" or existing_policy == "multiple":
            return ["Senior Agent", "Expert Agent"]

        # Straightforward purchase requests start with an Intent Agent. Complex
        # cases have already escalated above, regardless of purchase intent.
        if intent == "purchase" or (intent is None and purchase_intent == "high"):
            return ["Intent Agent", "Experienced Agent"]

        # Comparisons are the clearest available signal of shopping complexity.
        # Keep the thresholds explicit so routing is explainable to the UI.
        if comparison_count is not None:
            if comparison_count >= 4:
                return ["Senior Agent", "Expert Agent"]
            if comparison_count >= 2:
                return ["Experienced Agent", "Expert Agent"]

        if complexity == "medium":
            return ["Experienced Agent", "Expert Agent"]

        if intent == "agent_request":
            return ["Experienced Agent", "Expert Agent", "Senior Agent"]

        return ["Intent Agent", "Experienced Agent"]

    @staticmethod
    def required_level(roles):
        if not roles:
            return "Unassigned"
        if roles[0] == "Senior Agent":
            return "Senior/Expert Agent"
        if roles[0] == "Experienced Agent":
            return "Experienced Agent"
        return "Intent Agent"

    def assign(self, analysis, language="English"):
        domain = analysis["domain"]
        roles = self.required_role(analysis)
        required_level = self.required_level(roles)

        candidates = self.agents[
            (self.agents["availability"]) &
            (self.agents["domains_set"].apply(lambda s: domain in s or "general" in s))
        ].copy()

        if candidates.empty:
            return {
                "assigned": False,
                "reason": "No available agent for this domain",
                "required_level": required_level,
                "agent": None
            }

        # Prefer requested role, but allow fallback if no exact role is available.
        candidates["role_priority"] = candidates["role"].apply(
            lambda r: roles.index(r) if r in roles else len(roles) + 1
        )
        candidates["language_match"] = candidates["languages_set"].apply(
            lambda s: 1 if language in s else 0
        )
        candidates["domain_match"] = candidates["domains_set"].apply(
            lambda s: 1 if domain in s else 0
        )
        candidates["workload_ratio"] = candidates["current_workload"] / candidates["max_workload"].clip(lower=1)

        candidates = candidates.sort_values(
            by=["role_priority", "language_match", "domain_match", "workload_ratio", "experience_years"],
            ascending=[True, False, False, True, False]
        )

        selected = candidates.iloc[0]

        # A transparent matching score for UI/audit purposes.
        score = (
            40 * int(selected["domain_match"]) +
            25 * int(selected["language_match"]) +
            20 * (1 - float(selected["workload_ratio"])) +
            15 * min(float(selected["experience_years"]) / 10.0, 1.0)
        )

        return {
            "assigned": True,
            "reason": f"Matched {domain} domain, case complexity={analysis['complexity']}, role={selected['role']}",
            "required_level": required_level,
            "agent": {
                "agent_id": selected["agent_id"],
                "name": selected["name"],
                "role": selected["role"],
                "domains": selected["domains"],
                "languages": selected["languages"],
                "availability": bool(selected["availability"]),
                "specialization": selected["domains"],
                "experience_years": int(selected["experience_years"]),
                "current_workload": int(selected["current_workload"]),
                "match_score": round(float(score), 2)
            }
        }
