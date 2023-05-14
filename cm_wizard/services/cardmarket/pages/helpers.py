import re
from typing import TypeVar

from bs4 import Tag


def try_parse_euro_cents(text: str) -> int | None:
    unit_matches = re.findall(r"\d+", text)
    if len(unit_matches) == 0:
        return None
    return int(f"{unit_matches[0]}{unit_matches[1]}")


def parse_euro_cents(text: str) -> int:
    result = try_parse_euro_cents(text)
    assert result is not None, f'Could not parse price from text "{text}".'
    return result


B = TypeVar("B", bool, None)


def parse_bool(text: str, default: B) -> bool | B:
    match text.strip():
        case "Y":
            return True
        case "N":
            return False
    return default


def strip_multi_spaces(text: str):
    return re.sub(r"\s\s+", " ", text)


def extract_tooltip_image_url(tooltip: Tag) -> str:
    tooltip_title = tooltip.attrs["title"]
    image_url_match = re.search(r"src=\"(?P<image_url>.*?)\"", tooltip_title)
    assert (
        image_url_match is not None
    ), f'Image URL not found in tooltip title "{tooltip_title}".'
    return f"https:{image_url_match.group('image_url')}"


def find_tooltip(container: Tag) -> Tag:
    return container.find(attrs={"data-toggle": "tooltip"})
