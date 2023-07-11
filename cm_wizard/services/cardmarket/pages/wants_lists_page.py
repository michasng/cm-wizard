import logging
import re
from functools import cached_property

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.pages.html_element import (
    HtmlChildElement,
    HtmlPageElement,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class WantsListsPage(HtmlPageElement):
    @cached_property
    def items(self) -> list["WantsListsPageItem"]:
        cards: ResultSet[Tag] = self._tag.find_all(class_="card")
        _logger.info(f"{len(cards)} wants lists found.")
        return [WantsListsPageItem(self, card) for card in cards]


class WantsListsPageItem(HtmlChildElement[WantsListsPage]):
    @cached_property
    def id(self) -> str:
        link_tag = self._tag.find(class_="card-link-img-top")
        id_match = re.search(r"(?P<id>\d+)$", link_tag.attrs["href"])
        assert id_match is not None, f'ID not found in URL "{link_tag.attrs["href"]}".'
        return id_match.group("id")

    @cached_property
    def title(self) -> str:
        return self._tag.find(class_="card-title").text

    @cached_property
    def _cards_counts(self) -> list[str]:
        subtitle = self._tag.find(class_="card-subtitle").text
        matches = re.findall(r"\d+", subtitle)
        assert len(matches) == 2, f"Could not find counts in subtitle {subtitle}"
        return matches

    @cached_property
    def distinct_cards_count(self) -> int:
        return int(self._cards_counts[0])

    @cached_property
    def cards_count(self) -> int:
        return int(self._cards_counts[1])

    @cached_property
    def image_url(self) -> str:
        img = self._tag.find("img")
        url = img.attrs["data-echo"]
        return url if url.startswith("http") else f"https:{url}"
