"""Offline checks for LEI, ISIN and BIC strings (no network calls)."""
import re

LEI_RE = re.compile(r"^[A-Z0-9]{18}[0-9]{2}$")
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
BIC_RE = re.compile(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$")


def _letters_to_digits(s: str) -> str:
    """A=10, B=11, ... Z=35; digits stay as they are."""
    return "".join(str(int(c, 36)) for c in s)


def is_valid_lei(lei: str) -> bool:
    """ISO 17442: the 20-character code, read as a number, mod 97 must equal 1."""
    lei = lei.strip().upper()
    return bool(LEI_RE.match(lei)) and int(_letters_to_digits(lei)) % 97 == 1


def is_valid_isin(isin: str) -> bool:
    """ISO 6166: convert letters to numbers, then run the Luhn check."""
    isin = isin.strip().upper()
    if not ISIN_RE.match(isin):
        return False
    digits = _letters_to_digits(isin)
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def normalize_bic(bic: str) -> str | None:
    """Uppercase, drop spaces, and expand 8-character BICs to 11 with 'XXX'.

    GLEIF stores 11-character BICs, so 'DEUTDEFF' only matches as 'DEUTDEFFXXX'.
    Returns None if the string isn't shaped like a BIC.
    """
    bic = bic.replace(" ", "").strip().upper()
    if not BIC_RE.match(bic):
        return None
    return bic + "XXX" if len(bic) == 8 else bic


if __name__ == "__main__":
    for value in ["7LTWFZYICNSX8D621K86", "7LTWFZYICNSX8D621K87"]:
        print(f"LEI  {value}: {is_valid_lei(value)}")
    for value in ["US0378331005", "US0378331006"]:
        print(f"ISIN {value}: {is_valid_isin(value)}")
    for value in ["deutdeff", "BNPA FRPP XXX", "not-a-bic"]:
        print(f"BIC  {value!r} -> {normalize_bic(value)}")
