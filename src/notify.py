"""
# v1.0.0
Discord webhook notifier. Posts a Discord embed for each new entry/match
signal. Webhook URL is read from the EALA_DISCORD_WEBHOOK env var — never
hardcoded, never logged.
"""

import os

import requests

WEBHOOK_ENV_VAR = "EALA_DISCORD_WEBHOOK"
REQUEST_TIMEOUT_SECS = 15

EMBED_COLOR_ENTRY = 0x1F8B4C   # green
EMBED_COLOR_MATCH = 0x3498DB   # blue


def _post_embed(webhook_url: str, title: str, description: str, color: int, url: str | None = None) -> None:
    embed = {
        "title": title,
        "description": description,
        "color": color,
    }
    if url:
        embed["url"] = url

    payload = {"embeds": [embed]}
    resp = requests.post(webhook_url, json=payload, timeout=REQUEST_TIMEOUT_SECS)
    resp.raise_for_status()


def notify_entry(signal: dict, webhook_url: str | None = None) -> None:
    """Entry signal: 'Alexandra Eala has entered [Tournament] ([level], starts [date])'."""
    webhook_url = webhook_url or os.environ.get(WEBHOOK_ENV_VAR)
    if not webhook_url:
        raise RuntimeError(f"{WEBHOOK_ENV_VAR} is not set — cannot notify")

    title = "Alex Eala — New Tournament Entry"
    description = (
        f"Alexandra Eala has entered **{signal.get('title')}** "
        f"({signal.get('level')}, starts {signal.get('start_date')})"
    )
    _post_embed(webhook_url, title, description, EMBED_COLOR_ENTRY, url=signal.get("website_url"))


def notify_match(signal: dict, webhook_url: str | None = None) -> None:
    """Match signal: 'Alexandra Eala's next match: vs [Opponent] ([Country]), [Round], [Tournament], scheduled [time]'."""
    webhook_url = webhook_url or os.environ.get(WEBHOOK_ENV_VAR)
    if not webhook_url:
        raise RuntimeError(f"{WEBHOOK_ENV_VAR} is not set — cannot notify")

    title = "Alex Eala — Next Match Confirmed"
    round_label = f"Round {signal.get('round_id')}" if signal.get("round_id") is not None else "Round TBD"
    description = (
        f"Alexandra Eala's next match: vs **{signal.get('opponent_name')}** "
        f"({signal.get('opponent_country')}), {round_label}, "
        f"{signal.get('title')}, scheduled {signal.get('match_timestamp')}"
    )
    _post_embed(webhook_url, title, description, EMBED_COLOR_MATCH, url=signal.get("website_url"))


def notify(signal: dict, webhook_url: str | None = None) -> None:
    """Dispatches to the correct notifier based on signal['type']."""
    if signal["type"] == "entry":
        notify_entry(signal, webhook_url)
    elif signal["type"] == "match":
        notify_match(signal, webhook_url)
    else:
        raise ValueError(f"Unknown signal type: {signal['type']!r}")
