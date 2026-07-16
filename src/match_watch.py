"""
# v1.0.0
Match watch — checks a tournament's matches/draw feed for an upcoming (state
"U") singles match involving Alex Eala. This is the "match/opponent confirmed"
signal (same event as "draw dropped" — there is no separate TBD-opponent
state to detect).
"""

from wta_client import get_tournament_matches

EALA_PLAYER_ID = "330332"


def match_dedup_key(event_id, match_id) -> str:
    """Dedup key: f'{EventID}:{MatchID}' — never re-notify on this key again,
    even as MatchState transitions U -> S -> F."""
    return f"{event_id}:{match_id}"


def _is_eala_upcoming_singles(match: dict, player_id: str = EALA_PLAYER_ID) -> bool:
    if match.get("MatchState") != "U":
        return False
    if match.get("DrawMatchType") != "S":
        return False
    if not match.get("MatchTimeStamp"):
        return False
    player_a = str(match.get("PlayerIDA", ""))
    player_b = str(match.get("PlayerIDB", ""))
    return player_id in (player_a, player_b)


def check_matches(tournament: dict, known_matches: set) -> list[dict]:
    """
    Checks a single tournament descriptor for upcoming singles matches
    involving Eala. Returns a list of NEW signal dicts (not already in
    known_matches) — normally 0 or 1, but returns all new ones found.
    """
    tournament_id = tournament["id"]
    year = tournament["year"]

    matches_json = get_tournament_matches(tournament_id, year)
    matches = matches_json.get("matches", []) or []

    signals = []
    for match in matches:
        if not _is_eala_upcoming_singles(match):
            continue

        event_id = match.get("EventID")
        match_id = match.get("MatchID")
        key = match_dedup_key(event_id, match_id)
        if key in known_matches:
            continue

        player_a = str(match.get("PlayerIDA", ""))
        if player_a == EALA_PLAYER_ID:
            opponent_name = f"{match.get('PlayerNameFirstB', '')} {match.get('PlayerNameLastB', '')}".strip()
            opponent_country = match.get("PlayerCountryB")
        else:
            opponent_name = f"{match.get('PlayerNameFirstA', '')} {match.get('PlayerNameLastA', '')}".strip()
            opponent_country = match.get("PlayerCountryA")

        signals.append({
            "type": "match",
            "key": key,
            "tournament_id": tournament_id,
            "year": year,
            "title": tournament.get("title"),
            "website_url": tournament.get("website_url"),
            "opponent_name": opponent_name or "TBD",
            "opponent_country": opponent_country,
            "round_id": match.get("RoundID"),
            "match_timestamp": match.get("MatchTimeStamp"),
            "court_name": match.get("CourtName"),
        })
    return signals
