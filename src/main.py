"""
# v1.0.0
Eala Schedule Watcher — orchestrator.

Daily job: discovery -> entry_watch -> match_watch -> notify -> state.save.
Read-only against the WTA API; only mutates state/state.json. No odds/market
enrichment, no browser automation — schedule-detection-and-notify only.

Per-tournament checks are isolated: if one tournament's players/matches call
fails or returns an unexpected shape, it is logged and skipped so the rest of
the run still completes.
"""

import sys
import traceback

from discovery import discover_tournaments
from entry_watch import check_entry
from match_watch import check_matches
from notify import notify
from state import load_state, save_state, as_sets


def run() -> int:
    state = load_state()
    known_entries, known_matches = as_sets(state)

    new_signals = []

    try:
        tournaments = discover_tournaments()
    except Exception:
        print("[FATAL] discovery failed:", file=sys.stderr)
        traceback.print_exc()
        return 1

    print(f"[info] discovered {len(tournaments)} tournaments in window")

    for tournament in tournaments:
        tid, year = tournament.get("id"), tournament.get("year")

        try:
            entry_signal = check_entry(tournament, known_entries)
            if entry_signal:
                new_signals.append(entry_signal)
                known_entries.add(entry_signal["key"])
        except Exception:
            print(f"[warn] entry check failed for tournament {tid}/{year}:", file=sys.stderr)
            traceback.print_exc()

        try:
            match_signals = check_matches(tournament, known_matches)
            for sig in match_signals:
                new_signals.append(sig)
                known_matches.add(sig["key"])
        except Exception:
            print(f"[warn] match check failed for tournament {tid}/{year}:", file=sys.stderr)
            traceback.print_exc()

    print(f"[info] {len(new_signals)} new signal(s) found")

    notify_failed = False
    for signal in new_signals:
        try:
            notify(signal)
            print(f"[info] notified: {signal['type']} — {signal['key']}")
        except Exception:
            notify_failed = True
            print(f"[error] notify failed for signal {signal.get('key')}:", file=sys.stderr)
            traceback.print_exc()

    state["known_entries"] = list(known_entries)
    state["known_matches"] = list(known_matches)
    save_state(state)

    return 1 if notify_failed else 0


if __name__ == "__main__":
    sys.exit(run())
