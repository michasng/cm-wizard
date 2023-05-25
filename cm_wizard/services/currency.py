import re


def try_parse_euro_cents(text: str) -> int | None:
    unit_matches = re.findall(r"\d+", text)
    if len(unit_matches) < 2:
        return None
    return int(f"{unit_matches[0]}{unit_matches[1]}")


def parse_euro_cents(text: str) -> int:
    result = try_parse_euro_cents(text)
    assert result is not None, f'Could not parse price from text "{text}".'
    return result


def format_price(euro_cents: int) -> str:
    euros = str(euro_cents // 100)
    cents = str(euro_cents % 100).rjust(2, "0")
    return f"{euros},{cents} €"
