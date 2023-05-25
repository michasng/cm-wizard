import re
from typing import TypeVar

from bs4 import Tag

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


def extract_card_id_from_url(url: str) -> str:
    id_match = re.search(
        r"Cards\/(?P<general_id>[\w-]+)|Singles\/[\w-]+\/(?P<product_id>[\w-]+)",
        url,
    )
    assert id_match is not None, f'Card ID not found in URL "{url}".'
    return id_match.group("general_id") or id_match.group("product_id")
