"""
# v1.0.0
WTA Tennis API HTTP client — thin wrapper around the confirmed live endpoints.

Endpoints (verified via live network capture, 2026-07-16):
  - GET /tennis/tournaments/?from={date}&to={date}&excludeLevels=ITF   (discovery)
  - GET /tennis/tournaments/{tournamentId}/{year}/players               (entry list)
  - GET /tennis/tournaments/{tournamentId}/{year}/matches                (draw / schedule feed)

No auth required. An `account: wta` header is sent to match observed browser
behavior, even though it was not strictly required in testing.
"""

import requests

BASE_URL = "https://api.wtatennis.com/tennis"
DEFAULT_HEADERS = {
    "account": "wta",
    "User-Agent": "eala-schedule-watcher/1.0 (+https://github.com/AIinterruptor/eala-schedule-watcher)",
    "Accept": "application/json",
}
REQUEST_TIMEOUT_SECS = 20


def _get(path: str, params: dict | None = None) -> dict | list:
    """GET helper: builds the full URL, applies default headers, raises on HTTP errors."""
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=DEFAULT_HEADERS, params=params, timeout=REQUEST_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def get_tournaments(from_date: str, to_date: str, exclude_levels: str = "ITF") -> dict:
    """
    Discovery: list tournaments in a date window.

    from_date / to_date: 'YYYY-MM-DD' strings.
    Returns the raw JSON dict (has a 'content' list of tournament objects).
    """
    params = {
        "from": from_date,
        "to": to_date,
        "excludeLevels": exclude_levels,
    }
    return _get("/tournaments/", params=params)


def get_tournament_players(tournament_id: str, year: str | int) -> dict:
    """
    Entry list for a tournament/year. Returns raw JSON dict with 'events' list,
    each containing 'eventPlayers' -> 'players' (list of player dicts with 'id').
    """
    return _get(f"/tournaments/{tournament_id}/{year}/players")


def get_tournament_matches(tournament_id: str, year: str | int) -> dict:
    """
    Draw / schedule feed for a tournament/year. No 'states' filter — returns
    all match rows regardless of state (upcoming/live/final).
    Returns raw JSON dict/list depending on API shape (caller normalizes).
    """
    return _get(f"/tournaments/{tournament_id}/{year}/matches")
