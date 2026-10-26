"""Map BIC and ISIN codes to LEIs with the public GLEIF API (no key needed)."""
import time

import requests

from identifiers import is_valid_isin, normalize_bic

API = "https://api.gleif.org/api/v1/lei-records"
session = requests.Session()
session.headers["Accept"] = "application/vnd.api+json"


def get(params: dict) -> dict:
    """GET with a polite retry on HTTP 429 (GLEIF allows 60 requests a minute)."""
    for attempt in range(4):
        r = session.get(API, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 10)) + attempt * 5)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Still rate-limited after 4 attempts")


def summarize(record: dict) -> dict:
    a = record["attributes"]
    return {
        "lei": a["lei"],
        "legal_name": a["entity"]["legalName"]["name"],
        "country": a["entity"]["legalAddress"]["country"],
        "lei_status": a["registration"]["status"],         # ISSUED, LAPSED, ...
        "next_renewal": a["registration"]["nextRenewalDate"][:10],
    }


def bics_to_lei(bics: list[str], chunk: int = 50) -> dict[str, dict | None]:
    """Batch lookup: the bic filter takes a comma-separated list, and each
    record lists its BICs, so one request can resolve many codes."""
    wanted = {b: normalize_bic(b) for b in bics}
    found: dict[str, dict] = {}
    codes = sorted({c for c in wanted.values() if c})
    for i in range(0, len(codes), chunk):
        part = codes[i:i + chunk]
        data = get({"filter[bic]": ",".join(part), "page[size]": 200})["data"]
        for rec in data:
            for code in rec["attributes"].get("bic") or []:
                if code in part:
                    found[code] = summarize(rec)
    return {b: found.get(c) if c else None for b, c in wanted.items()}


def isin_to_lei(isin: str) -> dict | None:
    """One request per ISIN: records don't include their ISINs, so a batch
    response can't tell you which ISIN matched which LEI."""
    isin = isin.strip().upper()
    if not is_valid_isin(isin):
        return None
    data = get({"filter[isin]": isin})["data"]
    return summarize(data[0]) if data else None


if __name__ == "__main__":
    for bic, hit in bics_to_lei(["DEUTDEFF", "BNPAFRPPXXX", "ZZZZGB2LXXX"]).items():
        print(f"{bic:<12} -> {hit['lei'] + '  ' + hit['legal_name'] if hit else 'no LEI found'}")
    for isin in ["US0378331005", "DE0007164600", "GB0002634946"]:
        hit = isin_to_lei(isin)
        print(f"{isin} -> {hit['lei'] + '  ' + hit['legal_name'] if hit else 'no LEI found'}")
