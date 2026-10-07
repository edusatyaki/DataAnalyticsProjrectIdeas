# 11 · Pro Kabaddi League Analysis (Statistics & EDA)

**Module:** Statistics and EDA (Python)  **Dataset:** [kabaddiPy](https://github.com/kabaddiPy/kabaddiPy), which compiles official PKL stats for Seasons 1–10 (2014 – Mar 2024)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

> ⚠️ **Why the Kaggle file is not used:** the suggested [Kaggle "all seasons" CSV](https://www.kaggle.com/datasets/sauravshahi/pro-kabaddi-all-seasons-match-data-2014-2024) is broken. All 10 "seasons" are identical copies of Season 10 (every season has the same 137 matches, dated Dec 2023 – Mar 2024, and 1,233 of its 1,370 rows are duplicates). Real match results were rebuilt from kabaddiPy's match JSON with [`scripts/build_matches.py`](scripts/build_matches.py).

## Files in `data/`

| File | Rows | What it is |
|---|---|---|
| **`pkl_matches_s1_s10.csv`** | 1,064 | One row per match: `season, game_id, match_name, match_date, stage` (League/Playoffs/Semi Final/Final…), `venue, team_1, score_1, team_2, score_2, winner` (or "Tie"), `margin, result_text` |
| **`pkl_player_match_points.csv`** | 13,737 | Points per player per match: `season, game_id, match_date, team, player_id, player_name, player_role, points` |
| `all_seasons_player_stats_rounded.csv` | 1,636 | Player × season totals and ranks: raid points, tackle points, super raids, high-5s, super-10s, averages… |
| `AllSeasons_AllTeams_RaiderSuccessRate.csv` | 840 | Raider × season: total vs successful raids, success % (S5+) |
| `AllSeasons_AllTeams_DefenderSuccessRate.csv` | 988 | Defender × season: total vs successful tackles, success % (S5+) |
| `PKL_AggregatedTeamStats.csv` | 116 | Team × season: ~50 aggregate stats and ranks |
| `ALL_Raider_Skills_Merged.csv` / `ALL_Defensive_Skills_Merged.csv` | 98 / 118 | Skill × season counts per team (wide, one column per team) |

Season sizes: S1–S4 have 60 matches each; S5–S6 have 138; S7–S10 have 137. **101 matches (9.5%) are ties.**

## What the data check found

- **Team names change across seasons:** `Dabang Delhi` → `Dabang Delhi K.C.`, `U.P. Yoddha` vs `U.P. Yoddhas`. Build a mapping dict before grouping by team.
- 12 teams from Season 5 onward, 8 before that. Normalise any "per season" comparison (win %, not wins).
- The success-rate CSVs store percentages as text (`"37%"`, and one column has corrupted values like `"13200%"`). Parse them carefully, or recompute from total and successful counts. There are trailing unnamed columns; drop them.
- `player_role` is often blank in older seasons.
- `player_id` is consistent across files, so use it (not name) to join.

## Step-by-step approach

1. **Load & clean:**
   - Normalise team names and parse dates
   - Derive `total_points = score_1 + score_2`, a `home/away` flag from venue city, and `is_playoff`
   - Reshape matches to a long "team-match" table (one row per team per match: points for, against, result)
2. **Descriptive stats:**
   - Points per match by season: mean, median, std (is the game getting higher-scoring?)
   - Distribution of winning margins; tie rate by season
   - Standings: wins, losses, ties and win % per team-season. Validate the champions against the Final rows
3. **Team analysis:**
   - The most consistent teams (win % mean and std across seasons)
   - Points scored vs conceded scatter
   - Home vs away win rate
4. **Player analysis:**
   - Top raiders and defenders all-time and per season
   - Raid success % vs volume (scatter, with a minimum-raids filter)
   - Super-10 frequency and the Pareto share of team points from the top 2 players
5. **Statistical tests:**
   - **Chi-square:** is winning independent of venue (home advantage)?
   - **t-test / ANOVA:** do average points per match differ between early (S1–4) and later seasons?
   - **Correlation:** team raid-success % vs win %, and tackle-success % vs win %
   - **Normality** (Shapiro / Q-Q) of match totals; a **CI** for the average margin
6. **Answer the "what wins games" question:** regress team win % on raid points, tackle points, all-outs and super tackles (from `PKL_AggregatedTeamStats`). Is offence or defence more predictive?
7. **Visual story:** a season trend dashboard (matplotlib/seaborn or plotly) with 8–10 charts.

## Deliverables

`pkl_eda.ipynb` and a short "What wins Kabaddi matches" report.
