"""Flatten kabaddiPy's Matches-Overview JSON (S1..S10) into two CSVs.

Source: https://github.com/kabaddiPy/kabaddiPy/tree/main/pypi/kabaddiPy/Matches-Overview
Usage:  python build_matches.py <folder with S1.json..S10.json> ../data
"""
import csv, json, sys
from datetime import datetime
from pathlib import Path

def parse_date(raw):
    """Seasons 1-9 use '7/28/2017T8:00:00TPM'; season 10 uses ISO '2023-12-02T20:00+05:30'."""
    day = raw.split("T")[0]
    fmt = "%Y-%m-%d" if "-" in day else "%m/%d/%Y"
    return datetime.strptime(day, fmt).date().isoformat()


src, out = Path(sys.argv[1]), Path(sys.argv[2])
matches, players = [], []
for season in range(1, 11):
    for m in json.load(open(src / f"S{season}.json"))["matches"]:
        if "Completed" not in (m.get("event_status") or ""):
            continue
        p = m.get("participants") or []
        if len(p) != 2:
            continue
        date = parse_date(m["start_date"])
        s1, s2 = int(p[0]["value"] or 0), int(p[1]["value"] or 0)
        winner = p[0]["name"] if s1 > s2 else p[1]["name"] if s2 > s1 else "Tie"
        matches.append([season, m["game_id"], m["event_name"], date, m.get("event_stage"), m.get("venue_name"),
                        p[0]["name"], s1, p[1]["name"], s2, winner, abs(s1 - s2), m.get("event_sub_status")])
        for team in p:
            for pl in team.get("players_involved") or []:
                players.append([season, m["game_id"], date, team["name"], pl["id"], pl["name"], pl.get("type") or "", int(pl["value"] or 0)])

with open(out / "pkl_matches_s1_s10.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["season", "game_id", "match_name", "match_date", "stage", "venue", "team_1", "score_1",
                "team_2", "score_2", "winner", "margin", "result_text"])
    w.writerows(matches)
with open(out / "pkl_player_match_points.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["season", "game_id", "match_date", "team", "player_id", "player_name", "player_role", "points"])
    w.writerows(players)
print(len(matches), "matches,", len(players), "player-match rows")
