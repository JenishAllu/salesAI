"""
PolicyBuzar - Intelligent Agent Matching Engine
Implements the multi-criteria agent allocation rules specified in PART 11.
Considers:
1. Required Agent Level (Intern / Expert / Senior Expert) - NEVER silently downgraded.
2. Online & Available Status (online=True, status='Available')
3. Insurance Specialization (matching customer primary domain)
4. Supported Language (matching customer language preference)
5. Current Workload vs Max Workload (capacity headroom)
6. Years of Experience & Performance Rating
Provides complete assignment explanation, queueing fallback if qualified agents are at capacity.
"""

from backend.database.db_service import db_service


def match_agent(required_level, primary_domain, language):
    all_agents = db_service.get_all_agents()

    if not all_agents:
        return {
            "agent_id": "QUEUE-001",
            "agent_name": "Priority Routing Queue",
            "agent_level": required_level,
            "specializations": [primary_domain],
            "supported_languages": [language],
            "experience_years": 0,
            "is_online": False,
            "availability_status": "Queued",
            "current_workload": 0,
            "max_workload": 0,
            "performance_rating": 5.0,
            "match_score": 0,
            "reason": "No agent records found in database. Customer placed in priority queue."
        }

    # Level matching (Mandatory: do not downgrade)
    level_matched = [a for a in all_agents if a.get("agent_level") == required_level]

    if not level_matched:
        # If no agents at this tier exist at all
        return {
            "agent_id": "OVERFLOW-001",
            "agent_name": f"{required_level} Queue",
            "agent_level": required_level,
            "specializations": [primary_domain],
            "supported_languages": [language],
            "experience_years": 0,
            "is_online": False,
            "availability_status": "Queued",
            "current_workload": 0,
            "max_workload": 0,
            "performance_rating": 5.0,
            "match_score": 0,
            "reason": f"All {required_level} positions are currently unstaffed. Case escalated to supervisor queue."
        }

    # Score each candidate agent based on criteria
    scored_candidates = []
    for agent in level_matched:
        # Normalization
        specs = agent.get("specializations", [])
        if isinstance(specs, str):
            specs = [s.strip() for s in specs.split(",")]

        langs = agent.get("supported_languages", [])
        if isinstance(langs, str):
            langs = [l.strip() for l in langs.split(",")]

        is_online = bool(agent.get("is_online", False))
        status = agent.get("availability_status", "Offline")
        curr_wl = int(agent.get("current_workload", 0))
        max_wl = int(agent.get("max_workload", 5))
        exp = float(agent.get("experience_years", 1.0))
        rating = float(agent.get("performance_rating", 4.5))

        score = 0
        match_notes = []

        # Online & Availability check
        if is_online and status == "Available" and curr_wl < max_wl:
            score += 1000  # High baseline for available online agents
            match_notes.append("Online & Available")
        elif is_online and curr_wl < max_wl:
            score += 400
            match_notes.append(f"Online ({status})")
        else:
            score += 50
            match_notes.append("Offline or At Capacity")

        # Specialization matching
        if primary_domain in specs:
            score += 300
            match_notes.append(f"Specialized in {primary_domain}")
        elif "General" in specs:
            score += 100
            match_notes.append("General coverage specialization")

        # Language matching
        if language in langs:
            score += 350
            match_notes.append(f"Fluent in {language}")
        elif "English" in langs:
            score += 50
            match_notes.append("Fluent in English (Primary)")

        # Workload penalty (prefer lower workload)
        capacity_left = max(0, max_wl - curr_wl)
        score += capacity_left * 20

        # Experience & Performance boost
        score += min(exp, 15) * 5
        score += rating * 10

        scored_candidates.append({
            "agent": agent,
            "score": score,
            "notes": match_notes,
            "is_available": is_online and status == "Available" and curr_wl < max_wl,
            "specs": specs,
            "langs": langs
        })

    # Sort descending by match score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    best = scored_candidates[0]
    best_agent = best["agent"]

    # Construct human-readable assignment reason
    specs_str = ", ".join(best["specs"])
    langs_str = ", ".join(best["langs"])
    notes_str = "; ".join(best["notes"])

    if best["is_available"]:
        explanation = (
            f"Assigned {best_agent.get('agent_name')} ({best_agent.get('agent_id')} - {required_level}): "
            f"{notes_str}. Workload: {best_agent.get('current_workload')}/{best_agent.get('max_workload')}, "
            f"Experience: {best_agent.get('experience_years')} yrs, Rating: {best_agent.get('performance_rating')}."
        )
    else:
        explanation = (
            f"Notice: Highest-ranked {required_level} {best_agent.get('agent_name')} is currently {best_agent.get('availability_status')}. "
            f"Placed at front of priority queue for {primary_domain} ({language})."
        )

    return {
        "agent_id": best_agent.get("agent_id"),
        "agent_name": best_agent.get("agent_name"),
        "agent_level": required_level,
        "specializations": best["specs"],
        "supported_languages": best["langs"],
        "experience_years": best_agent.get("experience_years"),
        "is_online": best_agent.get("is_online"),
        "availability_status": best_agent.get("availability_status"),
        "current_workload": best_agent.get("current_workload"),
        "max_workload": best_agent.get("max_workload"),
        "performance_rating": best_agent.get("performance_rating"),
        "match_score": best["score"],
        "reason": explanation
    }
