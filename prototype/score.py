"""Deterministic scoring step (rules, no AI).

Input: structured fields produced by the AI extraction step (extracted.json).
Output: eligibility, per-criterion scores, total, status, and ranking.
Run: python score.py
"""
import json
from pathlib import Path

data = json.loads(Path(__file__).with_name("extracted.json").read_text())
cfg = data["category"]
W = cfg["criteria"]
props = data["proposals"]


def eligibility(p):
    if not p["licence_held"]:
        return "ineligible", "mandatory licence not held by bidder"
    if not p["wsib_and_insurance"]:
        return "ineligible", "WSIB/insurance not confirmed"
    if p["price"] > cfg["budget_ceiling"]:
        return "ineligible", "over budget ceiling"
    return "eligible", ""


elig = {k: eligibility(p) for k, p in props.items()}
passing = {k: p for k, p in props.items() if elig[k][0] == "eligible"}

min_price = min(p["price"] for p in passing.values())
weeks_ok = [p["weeks"] for p in passing.values() if p["weeks"] and p["weeks"] <= cfg["max_weeks"]]
min_weeks = min(weeks_ok)

results = {}
for k, p in props.items():
    status, why = elig[k]
    if status == "ineligible":
        results[k] = {"status": status, "rank": None, "score": None, "reason": why}
        continue
    parts = {}
    parts["experience"] = W["experience"] * min(p["installs_100kw_plus"], 12) / 12
    parts["price"] = W["price"] * min_price / p["price"]
    if p["weeks"] is None or p["weeks"] > cfg["max_weeks"]:
        parts["timeline"] = None
    else:
        parts["timeline"] = W["timeline"] * min_weeks / p["weeks"]
    parts["warranty"] = W["warranty"] * (
        0.5 * min(p["panel_warranty_years"] / 25, 1)
        + 0.5 * min(p["workmanship_warranty_years"] / 12, 1)
    )
    parts["team"] = W["team"] * sum(p["team"].values()) / 4
    flags = []
    if parts["timeline"] is None:
        flags.append("missing/invalid timeline")
    if p["injection_detected"]:
        flags.append("embedded instruction to the reviewer detected and ignored")
    total = None if parts["timeline"] is None else round(sum(parts.values()), 1)
    results[k] = {
        "status": "flagged" if flags else "ranked",
        "rank": None,
        "score": total,
        "parts": {a: (None if b is None else round(b, 2)) for a, b in parts.items()},
        "reason": "; ".join(flags),
    }

order = sorted(
    (k for k, r in results.items() if r["status"] == "ranked"),
    key=lambda k: (-results[k]["score"], k),  # tie-break: letter, fixed
)
for i, k in enumerate(order, 1):
    results[k]["rank"] = i

for k in sorted(results):
    print(k, json.dumps(results[k]))
