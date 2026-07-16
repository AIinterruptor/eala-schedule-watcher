"""
# v1.0.0
Entry watch — checks a tournament's players/entry-list endpoint for Alex
Eala's player id. New appearance (vs. known state) = "entered tournament"
signal.
"""

from wta_client import get_tournament_players

EALA_PLAYER_ID = "330332"


def entry_dedup_key(tournament_id, year) -> str:
    """Dedup key: one notification per tournament entry."""
    return f"{tournament_id}:{year}"


def player_in_entry_list(players_json: dict, player_id: str = EALA_PLAYER_ID) -> bool:
    """
    Checks events[].eventPlayers[].players[].id for the given player id.
    Player ids in the API payload are ints; compare as strings for safety.
    """
    for event in players_json.get("events", []) or []:
        for entry in event.get("eventPlayers", []) or []:
            for player in entry.get("players", []) or []:
                if str(player.get("id")) == str(player_id):
                    return True
    return False


def check_entry(tournament: dict, known_entries: set) -> dict | None:
    """
    Checks a single tournament descriptor (from discovery.discover_tournaments)
    for Eala's presence in the entry list. Returns a signal dict if this is a
    NEW entry (not already in known_entries), else None.
    """
    tournament_id = tournament["id"]
    year = tournament["year"]
    key = entry_dedup_key(tournament_id, year)

    if key in known_entries:
        return None

    players_json = get_tournament_players(tournament_id, year)
    if not player_in_entry_list(players_json):
        return None

    return {
        "type": "entry",
        "key": key,
        "tournament_id": tournament_id,
        "year": year,
        "title": tournament.get("title"),
        "level": tournament.get("level"),
        "start_date": tournament.get("start_date"),
        "website_url": tournament.get("website_url"),
    }
