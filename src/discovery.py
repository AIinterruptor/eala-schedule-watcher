"""
# v1.0.0
Discovery — scans a rolling date window (today -> +21 days) for candidate
tournaments, excluding ITF-level events. Returns normalized tournament
descriptors for entry_watch / match_watch to check.
"""

from datetime import date, timedelta

from wta_client import get_tournaments

WINDOW_DAYS = 21


def get_date_window(today: date | None = None) -> tuple[str, str]:
    """Returns (from_date, to_date) strings for the rolling discovery window."""
    if today is None:
        today = date.today()
    from_date = today.isoformat()
    to_date = (today + timedelta(days=WINDOW_DAYS)).isoformat()
    return from_date, to_date


def discover_tournaments(today: date | None = None) -> list[dict]:
    """
    Scans the rolling window and returns a normalized list of tournament
    descriptors: [{"id": ..., "year": ..., "title": ..., "level": ...,
    "start_date": ..., "website_url": ...}, ...]
    """
    from_date, to_date = get_date_window(today)
    raw = get_tournaments(from_date, to_date)
    content = raw.get("content", [])

    tournaments = []
    for item in content:
        group = item.get("tournamentGroup", {})
        metadata = group.get("metadata") or {}
        tournaments.append({
            "id": group.get("id"),
            "year": item.get("year"),
            "title": item.get("title"),
            "level": item.get("level"),
            "start_date": item.get("startDate"),
            "website_url": metadata.get("websiteUrl"),
        })
    return tournaments
