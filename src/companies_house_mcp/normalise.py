"""Normalise user input into the formats the Companies House API expects."""

import re
from typing import Annotated

from pydantic import AfterValidator

# [0-9] rather than \d: \d also matches non-ASCII digits like "٣".
_NUMERIC = re.compile(r"[0-9]{1,8}")
_PREFIXED = re.compile(r"([A-Z]{2})([0-9]{1,6})")


def normalise_company_number(raw: str) -> str:
    """Return the canonical 8-character company number, or raise ValueError.

    Examples: "445790" -> "00445790", "sc 12345" -> "SC012345".
    """
    cleaned = "".join(raw.split()).upper()

    if _NUMERIC.fullmatch(cleaned):
        return cleaned.zfill(8)

    prefixed = _PREFIXED.fullmatch(cleaned)
    if prefixed:
        prefix, digits = prefixed.groups()
        return prefix + digits.zfill(6)

    # The message is written for the model: say what's wrong and what to do next.
    shown = raw[:40]
    raise ValueError(
        f"{shown!r} is not a valid UK company number. Expected up to 8 digits "
        "(e.g. 00445790) or two letters followed by up to 6 digits (e.g. SC012345). "
        "To find a company by name, use search_company."
    )


# Use as a type on tool inputs: pydantic normalises the value during validation.
CompanyNumber = Annotated[str, AfterValidator(normalise_company_number)]
