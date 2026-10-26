# gleif-lei-python-examples

Small Python examples for mapping **BIC** and **ISIN** codes to **LEIs** (Legal Entity Identifiers) with the public [GLEIF API](https://documenter.getpostman.com/view/7679680/SVYrrxuU). No API key or account needed.

| File | What it does |
|---|---|
| `identifiers.py` | Offline checks: LEI check digits (ISO 17442), ISIN Luhn check (ISO 6166), BIC shape and 8→11 character normalisation |
| `gleif.py` | `bics_to_lei()` (batched) and `isin_to_lei()` (one request per ISIN) |
| `map_csv.py` | Adds `lei`, `legal_name`, `country`, `lei_status`, `next_renewal` and `match` columns to a CSV with `bic` and/or `isin` columns |
| `sample_input.csv` | Six example rows, including one ISIN typo and one unknown BIC |

## Quick start

Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python identifiers.py                          # offline checks
python gleif.py                                # BIC and ISIN lookups
python map_csv.py sample_input.csv out.csv     # enrich a CSV
```

## Real output (26 October 2026)

`python gleif.py`:
```
DEUTDEFF     -> 7LTWFZYICNSX8D621K86  DEUTSCHE BANK AKTIENGESELLSCHAFT
BNPAFRPPXXX  -> R0MUWSFPU8MPRO8K5P83  BNP PARIBAS
ZZZZGB2LXXX  -> no LEI found
US0378331005 -> HWUPKR0MPOU8FGXBT394  Apple Inc.
DE0007164600 -> 529900D6BF99LW9R2E68  SAP SE
GB0002634946 -> 8SVCSVKSGDWMW2QHOH83  BAE SYSTEMS PLC
```

`python map_csv.py sample_input.csv out.csv`:
```
4/6 rows matched -> out.csv

name,bic,isin,lei,legal_name,country,lei_status,next_renewal,match
Deutsche Bank,DEUTDEFF,,7LTWFZYICNSX8D621K86,DEUTSCHE BANK AKTIENGESELLSCHAFT,DE,ISSUED,2027-06-02,bic
BNP Paribas,BNPAFRPPXXX,,R0MUWSFPU8MPRO8K5P83,BNP PARIBAS,FR,ISSUED,2027-02-06,bic
Apple,,US0378331005,HWUPKR0MPOU8FGXBT394,Apple Inc.,US,ISSUED,2027-03-08,isin
SAP,,DE0007164600,529900D6BF99LW9R2E68,SAP SE,DE,ISSUED,2027-01-26,isin
Typo example,,US0378331006,,,,,,invalid_isin
Unknown BIC,ZZZZGB2LXXX,,,,,,,none
```

LEI data changes over time (renewal dates, statuses), so your output may differ.

## Notes

- **8-character BICs** only match after padding to 11 characters with `XXX`; `normalize_bic()` does that.
- **ISINs are looked up one at a time.** The `filter[isin]` parameter accepts a list, but LEI records don't include their ISINs, so a batch response can't be matched back to the input codes.
- **Rate limit:** GLEIF's documentation says "Rate limiting is currently set at 60 requests, per minute, per user, for all users." `gleif.py` retries on HTTP 429 and `map_csv.py` paces ISIN lookups.
- **Large lists:** GLEIF publishes downloadable [BIC-to-LEI and ISIN-to-LEI relationship files](https://www.gleif.org/en/lei-data/lei-mapping) for local joins.
- **Data licence:** GLEIF's [terms of use](https://www.gleif.org/en/meta/lei-data-terms-of-use) say LEI data "are provided under the CC0 licence".

## License

Code: MIT (see `LICENSE`).
