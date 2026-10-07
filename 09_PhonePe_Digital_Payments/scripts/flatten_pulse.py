"""Flatten PhonePe Pulse JSON (https://github.com/PhonePe/pulse) into state-level CSVs.

Usage:
    git clone --depth 1 https://github.com/PhonePe/pulse.git
    python flatten_pulse.py pulse/data ../data
"""
import csv, json, sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)


def state_files(kind, metric, hover=False):
    base = src / kind / metric / ("hover/country/india/state" if hover else "country/india/state")
    for f in sorted(base.glob("*/*/*.json")):
        state, year, q = f.parts[-3], int(f.parts[-2]), int(f.stem)
        yield state, year, q, json.load(open(f)).get("data") or {}


def write(name, header, rows):
    # The current Pulse schema dropped some fields (e.g. amount in aggregated/top, appOpens); drop all-empty columns
    keep = [i for i in range(len(header)) if any(r[i] is not None for r in rows)]
    header, rows = [header[i] for i in keep], [[r[i] for i in keep] for r in rows]
    with open(out / f"{name}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


# aggregated/transaction -> category totals per state-quarter
rows = []
for st, y, q, d in state_files("aggregated", "transaction"):
    for t in d.get("transactionData") or []:
        for pi in t.get("paymentInstruments") or []:
            rows.append([st, y, q, t["name"], pi.get("count"), pi.get("amount")])
write("aggregated_transaction", ["state", "year", "quarter", "transaction_type", "count", "amount"], rows)

# aggregated/user and aggregated/merchant -> registered counts (+ app opens / device brands when present)
for metric in ("user", "merchant"):
    rows, brands = [], []
    for st, y, q, d in state_files("aggregated", metric):
        a = d.get("aggregated") or {}
        rows.append([st, y, q, a.get("registeredCount") or a.get("registeredUsers"), a.get("appOpens")])
        for b in d.get("usersByDevice") or []:
            brands.append([st, y, q, b.get("brand"), b.get("count"), b.get("percentage")])
    write(f"aggregated_{metric}", ["state", "year", "quarter", "registered_count", "app_opens"], rows)
    if brands:
        write(f"aggregated_{metric}_by_device", ["state", "year", "quarter", "brand", "count", "percentage"], brands)

# map/transaction -> district count & amount
rows = []
for st, y, q, d in state_files("map", "transaction", hover=True):
    for h in d.get("hoverDataList") or []:
        for m in h.get("metric") or []:
            rows.append([st, y, q, h["name"], m.get("count"), m.get("amount")])
write("map_transaction", ["state", "year", "quarter", "district", "count", "amount"], rows)

# map/user and map/merchant -> district registered counts
for metric in ("user", "merchant"):
    rows = []
    for st, y, q, d in state_files("map", metric, hover=True):
        for district, v in (d.get("hoverData") or {}).items():
            rows.append([st, y, q, district, v.get("registeredCount") or v.get("registeredUsers"), v.get("appOpens")])
    write(f"map_{metric}", ["state", "year", "quarter", "district", "registered_count", "app_opens"], rows)

# top/* -> top districts and pincodes
for metric in ("transaction", "user", "merchant"):
    rows = []
    for st, y, q, d in state_files("top", metric):
        for level in ("districts", "pincodes"):
            for e in d.get(level) or []:
                m = e.get("metric") or {}
                rows.append([st, y, q, level[:-1], e.get("entityName") or e.get("name"),
                             m.get("count"), m.get("amount"), e.get("registeredCount") or e.get("registeredUsers")])
    write(f"top_{metric}", ["state", "year", "quarter", "level", "entity", "count", "amount", "registered_count"], rows)
