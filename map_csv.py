"""Add LEI columns to a CSV that has a 'bic' and/or 'isin' column.

Usage: python map_csv.py input.csv output.csv
"""
import csv
import sys
import time

from gleif import bics_to_lei, isin_to_lei
from identifiers import is_valid_isin, normalize_bic

FIELDS = ["lei", "legal_name", "country", "lei_status", "next_renewal", "match"]


def main(src: str, dst: str) -> None:
    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    bic_hits = bics_to_lei([r["bic"] for r in rows if r.get("bic")])

    isin_hits = {}
    for isin in {r["isin"] for r in rows if r.get("isin")}:
        isin_hits[isin] = isin_to_lei(isin)
        time.sleep(1.1)  # stay under 60 requests a minute

    for r in rows:
        hit, how = None, ""
        if r.get("bic") and bic_hits.get(r["bic"]):
            hit, how = bic_hits[r["bic"]], "bic"
        elif r.get("isin") and isin_hits.get(r["isin"]):
            hit, how = isin_hits[r["isin"]], "isin"
        if not hit and r.get("isin") and not is_valid_isin(r["isin"]):
            how = "invalid_isin"
        elif not hit and r.get("bic") and not normalize_bic(r["bic"]):
            how = "invalid_bic"
        r.update({k: (hit or {}).get(k, "") for k in FIELDS[:-1]})
        r["match"] = how or "none"

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{sum(r['match'] in ('bic', 'isin') for r in rows)}/{len(rows)} rows matched -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
