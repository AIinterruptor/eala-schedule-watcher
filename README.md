# Eala Schedule Watcher

A GitHub Actions bot that checks Alexandra Eala's (WTA player id `330332`)
tournament schedule daily and posts a Discord notification when something new
is found. Read-only, notification-only — no odds/market enrichment, no
trading logic, no browser automation.

## What it detects

1. **Tournament entry** — Eala appears in a tournament's entry list
   (`/tennis/tournaments/{id}/{year}/players`) for the first time.
2. **Match confirmed** — an upcoming singles match (`MatchState: "U"`)
   involving Eala appears in a tournament's draw/schedule feed
   (`/tennis/tournaments/{id}/{year}/matches`). This is the same event as
   "draw dropped" — there's no separate TBD-opponent state.

Discovery scans a rolling window (today → +21 days) via
`/tennis/tournaments/?from=...&to=...&excludeLevels=ITF`, then checks each
candidate tournament's players/matches feeds.

## Structure

```
src/
  wta_client.py    HTTP wrapper for the 3 WTA API endpoints
  discovery.py     date-range scan -> candidate tournaments
  entry_watch.py   entry-list check -> "entered tournament" signal
  match_watch.py   draw/schedule check -> "match confirmed" signal
  notify.py        Discord webhook POST
  state.py         load/save state/state.json, dedup helpers
  main.py          orchestrates the full run
state/state.json  committed dedup state
```

## Dedup

- Entry key: `f"{tournamentId}:{year}"` — one notification per tournament entry.
- Match key: `f"{EventID}:{MatchID}"` — notified once, never again even as
  `MatchState` transitions U → S → F.

`state/state.json` is committed back to the repo by the workflow after each
run — no external database.

## Schedule

Runs once daily via `on: schedule` (`0 6 * * *`, UTC). Can also be triggered
manually via `workflow_dispatch` for testing.

## Secrets

- `EALA_DISCORD_WEBHOOK` — Discord webhook URL for notifications. Set via
  `gh secret set EALA_DISCORD_WEBHOOK`. Never hardcoded in source.

The workflow's own state-commit step uses the default `GITHUB_TOKEN`
(scoped `contents: write`) — no PAT required for that step.
