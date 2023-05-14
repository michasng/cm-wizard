import logging
import re
from functools import cached_property

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.pages.card_product_info import CardProductInfo
from cm_wizard.services.cardmarket.pages.helpers import (
    extract_card_id_from_url,
    extract_tooltip_image_url,
    find_tooltip,
    parse_euro_cents,
)
from cm_wizard.services.cardmarket.pages.html_element import (
    HtmlChildElement,
    HtmlPageElement,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SellerOffersPage(HtmlPageElement):
    @cached_property
    def _main(self) -> Tag:
        return self._tag.find("body").find("main")

    @cached_property
    def _page_title_container(self) -> Tag:
        return self._main.find(class_="page-title-container")

    @cached_property
    def _h1(self) -> Tag:
        return self._page_title_container.find("h1")

    @cached_property
    def id(self) -> str:
        return self._h1.find(string=True, recursive=False).get_text(strip=True)

    @cached_property
    def country(self) -> str:
        return find_tooltip(self._h1).attrs["data-original-title"]

    @cached_property
    def eta_days(self) -> int | None:
        eta_days = int(self._page_title_container.find(class_="h3").text)
        if eta_days == 0:
            # if cardmarket does not have enough data, they still write "0 days to you"
            return None
        return eta_days

    @cached_property
    def _section(self) -> Tag:
        return self._main.find("section")

    @cached_property
    def _pagination(self) -> Tag:
        return self._section.find(class_="pagination")

    @cached_property
    def total_count(self) -> int:
        return int(self._pagination.find(class_="total-count").text)

    @cached_property
    def _pagination_counts(self) -> list[int]:
        label = self._pagination.find("span", class_="mx-1").text
        counts = re.findall(r"\d+", label)
        assert len(counts) == 2, 'Could not find page counts in label "{label}".'
        return [int(count) for count in counts]

    @cached_property
    def current_page(self) -> int:
        return self._pagination_counts[0]

    @cached_property
    def total_page_count(self) -> int:
        return self._pagination_counts[1]

    @cached_property
    def offers(self) -> list["SellerSinglesPageOffer"]:
        table = self._section.find(id="UserOffersTable")
        rows: ResultSet[Tag] = table.find(class_="table-body").find_all(
            class_="article-row"
        )
        _logger.info(f"{len(rows)} offers found.")
        return [SellerSinglesPageOffer(self, row) for row in rows]


class SellerSinglesPageOffer(HtmlChildElement[SellerOffersPage]):
    @cached_property
    def image_url(self) -> str:
        tooltip = find_tooltip(self._tag.find(class_="col-thumbnail"))
        return extract_tooltip_image_url(tooltip)

    @cached_property
    def _col_seller_product_info(self) -> Tag:
        return self._tag.find(class_="col-sellerProductInfo")

    @cached_property
    def _name_link_tag(self) -> Tag:
        return self._col_seller_product_info.find(class_="col-seller").find("a")

    @cached_property
    def id(self) -> str:
        return extract_card_id_from_url(str(self._name_link_tag.attrs["href"]))

    @cached_property
    def name(self) -> str:
        return self._name_link_tag.text

    @cached_property
    def product(self) -> "CardProductInfo":
        product_column = self._col_seller_product_info.find(class_="col-product")
        return CardProductInfo(self, product_column)

    @cached_property
    def _col_offer(self) -> Tag:
        return self._tag.find(class_="col-offer")

    @cached_property
    def price_euro_cents(self) -> int:
        container = self._col_offer.find(class_="price-container")
        return parse_euro_cents(container.text)

    @cached_property
    def quantity(self) -> int:
        container = self._col_offer.find(class_="amount-container")
        return int(container.text)
