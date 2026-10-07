# 11 · Pro Kabaddi League Analysis

**Module:** Statistics and EDA (Python)  **Dataset:** [kabaddiPy](https://github.com/kabaddiPy/kabaddiPy), compiled official PKL stats for Seasons 1–10 (2014 – Mar 2024)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

> ⚠️ **Why the Kaggle file is not used:** the suggested [Kaggle "all seasons" CSV](https://www.kaggle.com/datasets/sauravshahi/pro-kabaddi-all-seasons-match-data-2014-2024) is broken. All 10 "seasons" are copies of Season 10 (1,233 of 1,370 rows are duplicates). Real results were rebuilt from kabaddiPy's match JSON with [`scripts/build_matches.py`](scripts/build_matches.py). Spotting this kind of problem is the first lesson of the project.

---

## 1. Project description

**Business context.** A PKL franchise's analytics staff wants evidence for team-building and match strategy: has the game changed over 10 seasons, which teams and players perform consistently, does home advantage exist, and is it raiding (attack) or tackling (defence) that wins matches?

**Objective.** Clean and combine match-, player- and team-level data, run descriptive and inferential statistics, and present "what wins Kabaddi matches" with evidence.

**Stakeholders.** Team management, coaches, scouts, broadcasters and fantasy-sports analysts.

**Key questions**
1. How have scoring, margins and ties changed across seasons?
2. Which teams are most successful and most consistent? Who won each final?
3. Who are the top players of all time, and how dependent are teams on their stars?
4. Is there a home advantage?
5. Does raiding or defending correlate more with winning?

## 2. Dataset

| File | Rows | What it is |
|---|---|---|
| **`pkl_matches_s1_s10.csv`** | 1,064 | One row per match: `season, game_id, match_name, match_date, stage, venue, team_1, score_1, team_2, score_2, winner` ("Tie" if level), `margin, result_text` |
| **`pkl_player_match_points.csv`** | 13,737 | Points per player per match: `season, game_id, match_date, team, player_id, player_name, player_role, points` |
| `all_seasons_player_stats_rounded.csv` | 1,636 | Player × season totals and ranks |
| `AllSeasons_AllTeams_RaiderSuccessRate.csv` | 840 | Raider × season: total/successful raids (S5+) |
| `AllSeasons_AllTeams_DefenderSuccessRate.csv` | 988 | Defender × season: total/successful tackles (S5+) |
| `PKL_AggregatedTeamStats.csv` | 116 | Team × season: ~50 aggregate stats (raid/tackle points, all-outs, success %) |
| `ALL_Raider_Skills_Merged.csv` / `ALL_Defensive_Skills_Merged.csv` | 98 / 118 | Skill counts per team (wide format) |

Season sizes: S1–S4 had 8 teams and 60 matches; S5–S10 had 12 teams and 137–138 matches.

---

## 3. Data cleaning

| # | Issue | Fix |
|---|---|---|
| 1 | Broken Kaggle file (duplicated seasons) | Rebuilt from source JSON. Check: `df.drop(columns='season').duplicated().sum()` should be 0 |
| 2 | **Team names change**: `Dabang Delhi` → `Dabang Delhi K.C.`, `U.P. Yoddhas` vs `U.P. Yoddha` | Mapping dict applied to `team_1`, `team_2`, `winner`, `team` columns |
| 3 | **Venue names are inconsistent** (42 spellings: "DOME,NSCI,SVP STADIUM,MUMBAI", "‘DOME, NSCI SVP STADIUM’"…, some with no city) | Keyword → city map (NSCI → Mumbai, Thyagaraj → Delhi, Netaji → Kolkata, Sheraton Whitefield → Bengaluru bio-bubble S8…) |
| 4 | Dates in two source formats (S1–9 `7/28/2017T…`, S10 ISO) | Parsed to ISO dates in the build script |
| 5 | Ties stored as a scoreline | `winner = "Tie"`; result column W/L/T per team |
| 6 | Wide match table | Reshape to a **team-match long table** (2 rows per match: points for, against, result) |
| 7 | `PKL_AggregatedTeamStats.csv` contains `season = "all"` summary rows | Drop them before season analysis; cast season to int |
| 8 | Success-rate CSVs store `%` as text; one column has corrupted values (`"13200%"`); trailing unnamed columns | `str.rstrip('%')`, recompute from total and successful counts, drop the `Unnamed:` columns |
| 9 | `player_role` blank for 35% of rows | Fill from the player-stats file using `player_id`, else "Unknown" |
| 10 | Join keys | Use `player_id`, not names (spellings vary) |

---

## 4. Exploratory data analysis (EDA)

**Season trends:** average total points per match, average margin and tie % by season (line charts); share of close games (margin ≤ 3).
**Teams:** standings per season (W/L/T, win %); all-time win % ranking; consistency = std of season win %; points for vs against scatter; list of finals and champions.
**Players:** all-time top scorers; Super-10s (≥ 10 points in a match) leaders; raid success % vs volume scatter (minimum-raids filter); top-2 players' share of team points (star dependence).
**Venues:** matches by city; neutral and bubble venues (S8 Bengaluru bubble, Kochi, Nagpur).
**What wins:** correlation of season win % with raid points, tackle points, all-outs inflicted and conceded, raid and tackle success % (from `PKL_AggregatedTeamStats`); heat map plus scatter plots.

---

## 5. Testing

**A. Data-validation tests**

| Test | Pass condition |
|---|---|
| No duplicated matches across seasons | 0 duplicates on (date, teams, scores) |
| Every final's winner matches the known champion list | 10/10 |
| `winner` consistent with scores | `winner == team with higher score`, or Tie when equal |
| Sum of player points per team-match ≤ team score | Holds for 2,092 of 2,094 (team score also includes all-out and extra points; median player share 77%). Inspect the 2 exceptions |
| After name mapping, 12 distinct teams | 12 |

**B. Statistical tests**

| # | Hypothesis (H₀) | Test | Result |
|---|---|---|---|
| 1 | Average match total is the same in S1–4 and S5–10 | Welch t-test | 61.9 vs 68.4 points, **p ≈ 2e-16. Reject:** scoring went up |
| 2 | No home advantage (home win rate = 50%) | Binomial test on 335 decisive home games | Home teams won **46.3%**, p = 0.19. **No home advantage** |
| 3 | Match totals are normally distributed | Shapiro-Wilk + Q-Q plot | p = 0.002, skew 0.44. Mildly right-skewed, so prefer non-parametric tests |
| 4 | Win % is unrelated to tackle points per match | Pearson correlation | **r = 0.50** (tackle success %: r = 0.67) |
| 5 | Win % is unrelated to raid points per match | Pearson correlation | r = 0.20 (raid success %: r = 0.29) |
| 6 | Win % is unrelated to points conceded | Pearson correlation | **r = −0.57** |
| 7 | Tie rate is the same across seasons | Chi-square on season × tie | p = 0.96. **Fail to reject:** the tie rate (6.7%–11.7%) is stable across seasons |

---

## 6. Observations (from this data)

1. **The game got higher-scoring:** points per match fell from 68 (S1) to about 59–60 (S2–S4), then rose steadily to **72 in S9 and S10**. Later seasons average 6.5 more points per match (significant).
2. **Close contests:** **34% of matches are decided by 3 points or fewer**, and ties are 6.7%–11.7% of matches each season (101 ties in total).
3. **Champions:** S1 Jaipur, S2 U Mumba, **S3–S5 Patna Pirates (three in a row)**, S6 Bengaluru, S7 Bengal Warriors, S8 Dabang Delhi, S9 Jaipur, S10 Puneri Paltan.
4. **Best all-time win %:** U Mumba 53.8%, Patna Pirates 52.5%, Gujarat Giants 52.5%. The weakest are Tamil Thalaivas 29.1% and Telugu Titans 29.2%.
5. **Consistency differs:** Tamil Thalaivas are consistently weak (season-to-season std 10 pp); Puneri Paltan are the most volatile (std 21.5 pp: from bottom of the table to champions).
6. **Star players:** Pardeep Narwal has the most points (1,236) and Super-10s (65), followed by Maninder Singh (1,021) and Rahul Chaudhari (953). On average a team's **top-2 scorers make 68% of its points** in a match.
7. **Defence wins:** season win % correlates **0.67 with tackle success %** and **0.50 with tackle points**, but only **0.29 with raid success %** and 0.20 with raid points. Conceding fewer points (r = −0.57) matters more than scoring more (0.48).
8. **No home advantage:** home teams won only 46% of decisive games (p = 0.19). The caravan format and neutral venues dilute it.

## 7. Recommendations

1. **Invest in defenders.** Tackle success is the strongest predictor of winning, yet raiders take the headline auction money, so defenders may be under-valued.
2. **Reduce star dependence:** with 68% of points from two players, an injury is devastating. Develop a third scoring option and squad depth.
3. **Train for close finishes:** a third of games are decided by ≤ 3 points. Practise last-minute decisions (do-or-die raids, super tackles).
4. **Don't count on home games:** plan strategy for every match equally; there is no measurable home edge.
5. **Scouting:** use season-level consistency (low std) with win % to pick reliable players; look at Patna's S3–S5 dynasty for roster continuity.
6. **League (for broadcasters):** rising scoring and frequent close games are a strong viewer story. Promote them.

## 8. Deliverables

`pkl_eda.ipynb` (cleaning log → EDA → tests table → "what wins" analysis) and a 2-page "What wins Kabaddi matches" report.
