"""
# v1.0.0
State load/save + dedup helpers. state/state.json is committed by the GitHub
Actions workflow after each run — simplest durable approach, no external DB.
"""

import json
import os

STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "state.json")

DEFAULT_STATE = {
    "known_entries": [],
    "known_matches": [],
}


def load_state(path: str = STATE_PATH) -> dict:
    """Loads state/state.json, returning the default shape if missing/corrupt."""
    if not os.path.exists(path):
        return dict(DEFAULT_STATE)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_STATE)

    data.setdefault("known_entries", [])
    data.setdefault("known_matches", [])
    return data


def save_state(state: dict, path: str = STATE_PATH) -> None:
    """Writes state back to disk, sorted for stable diffs."""
    out = {
        "known_entries": sorted(set(state.get("known_entries", []))),
        "known_matches": sorted(set(state.get("known_matches", []))),
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")


def as_sets(state: dict) -> tuple[set, set]:
    """Returns (known_entries_set, known_matches_set) for O(1) membership checks."""
    return set(state.get("known_entries", [])), set(state.get("known_matches", []))
