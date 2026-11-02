from importlib.metadata import version

import companies_house_mcp


def test_smoke() -> None:
    assert version("uk-companies-house-mcp") == companies_house_mcp.__version__
