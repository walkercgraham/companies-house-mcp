import pytest
from pydantic import TypeAdapter, ValidationError

from companies_house_mcp.normalise import CompanyNumber, normalise_company_number

VALID_CASES = [
    # (input, expected output)
    ("445790", "00445790"),
    ("1", "00000001"),
    ("00445790", "00445790"),
    (" 567890", "00567890"),
    ("567890 ", "00567890"),
    ("23456 7", "00234567"),
    ("sc 123", "SC000123"),
    ("SC 2376", "SC002376"),
    ("SC123456", "SC123456"),
    ("sc 901234", "SC901234"),
    ("NI123456", "NI123456"),
    ("oc301234", "OC301234"),
]

INVALID_CASES = [
    # inputs that must raise ValueError
    "",  # empty
    " ",  # only whitespace
    "TESCO",  # letters only
    "123977723",  # 9 digits
    "SC1234567",  # prefix with 7 digits
    "S12345",  # one-letter prefix
    "1A234567",  # letter after a digit
    "00-445790",  # symbols
]


@pytest.mark.parametrize(("raw", "expected"), VALID_CASES)
def test_valid_company_numbers(raw: str, expected: str) -> None:
    assert normalise_company_number(raw) == expected


@pytest.mark.parametrize("raw", INVALID_CASES)
def test_invalid_company_numbers(raw: str) -> None:
    with pytest.raises(ValueError):
        normalise_company_number(raw)


def test_error_message_points_to_search() -> None:
    with pytest.raises(ValueError, match="search_company"):
        normalise_company_number("TESCO")


def test_company_number_type_normalises_via_pydantic() -> None:
    adapter = TypeAdapter(CompanyNumber)
    assert adapter.validate_python("sc 12345") == "SC012345"
    with pytest.raises(ValidationError):
        adapter.validate_python("TESCO")
