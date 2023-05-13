import logging
import re
from functools import cached_property

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage
from cm_wizard.services.cardmarket.pages.helpers import (
    extract_tooltip_image_url,
    parse_bool,
    try_parse_euro_cents,
)
from cm_wizard.services.cardmarket.pages.html_element import (
    HtmlChildElement,
    HtmlPageElement,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class WantsListPage(HtmlPageElement):
    @cached_property
    def title(self) -> str:
        return self.tag.find("h1").text

    @cached_property
    def _table(self) -> Tag:
        return self.tag.find(class_="data-table")

    @cached_property
    def _table_column_indexes(self) -> dict[str, int]:
        table_header_row = self._table.find("thead")

        def find_bool_th(title: str) -> Tag | None:
            th_span = table_header_row.find("span", attrs={"title": title})
            if th_span is None:
                return None
            return th_span.parent

        return {
            key: table_header_row.index(th_tag) if th_tag is not None else None
            for key, th_tag in {
                "name": table_header_row.find(class_="name"),
                "preview": table_header_row.find(class_="preview"),
                "amount": table_header_row.find(class_="amount"),
                "expansion": table_header_row.find(class_="expansion"),
                "languages": table_header_row.find(class_="languages"),
                "min_condition": table_header_row.find(class_="condition"),
                "is_reverse_holo": find_bool_th("Reverse Holo?"),
                "is_signed": find_bool_th("Signed?"),
                "is_first_edition": find_bool_th("First Edition?"),
                "is_altered": find_bool_th("Altered?"),
                "buy_price": table_header_row.find(class_="buyPrice"),
                "has_mail_alert": table_header_row.find(class_="mailAlert"),
            }.items()
        }

    @cached_property
    def items(self) -> list["WantsListPageItem"]:
        table_body = self._table.find("tbody")
        rows: ResultSet[Tag] = table_body.find_all("tr")
        _logger.info(f"{len(rows)} wanted found.")
        return [WantsListPageItem(self, row) for row in rows]


class WantsListPageItem(HtmlChildElement[WantsListPage]):
    def _find_td(self, key: str) -> Tag:
        index = self.parent._table_column_indexes[key]
        return self.tag.contents[index]

    def _find_td_tooltips(self, key: str) -> ResultSet[Tag]:
        return self._find_td(key).find_all(
            attrs={"data-toggle": "tooltip"},
        )

    def _find_td_optional_bool(self, key: str) -> bool | None:
        index = self.parent._table_column_indexes[key]
        if index is None:
            return None
        text = self.tag.contents[index].text
        return parse_bool(text, default=None)

    @cached_property
    def _name_link_tag(self) -> Tag:
        return self._find_td("name").find("a")

    @cached_property
    def id(self) -> str:
        id_match = re.search(
            r"Cards\/(?P<general_id>[\w-]+)|Singles\/[\w-]+\/(?P<product_id>[\w-]+)",
            str(self._name_link_tag["href"]),
        )
        assert (
            id_match is not None
        ), f'Card ID not found in URL "{self._name_link_tag["href"]}".'
        return id_match.group("general_id") or id_match.group("product_id")

    @cached_property
    def name(self) -> str:
        return self._name_link_tag.text

    @cached_property
    def amount(self) -> int:
        return int(self._find_td("amount").text)

    @cached_property
    def image_url(self) -> str:
        return extract_tooltip_image_url(self._find_td("preview"))

    @cached_property
    def expansions(self) -> list[str] | None:
        tooltips = self._find_td_tooltips("expansion")
        return [tooltip.find("span").text for tooltip in tooltips]

    @cached_property
    def languages(self) -> list[CardLanguage] | None:
        tooltips = self._find_td_tooltips("languages")
        return [
            CardLanguage.find_by_label(
                self.parent.language, tooltip.attrs["data-original-title"]
            )
            for tooltip in tooltips
        ]

    @cached_property
    def min_condition(self) -> CardCondition:
        return CardCondition.find_by_abbreviation(
            self._find_td("min_condition").find(class_="badge").text
        )

    @cached_property
    def is_reverse_holo(self) -> bool | None:
        return self._find_td_optional_bool("is_reverse_holo")

    @cached_property
    def is_signed(self) -> bool | None:
        return self._find_td_optional_bool("is_signed")

    @cached_property
    def is_first_edition(self) -> bool | None:
        return self._find_td_optional_bool("is_first_edition")

    @cached_property
    def is_altered(self) -> bool | None:
        return self._find_td_optional_bool("is_altered")

    @cached_property
    def buy_price_euro_cents(self) -> int | None:
        return try_parse_euro_cents(self._find_td("buy_price").find("span").text)

    @cached_property
    def has_mail_alert(self) -> bool:
        return parse_bool(self._find_td("has_mail_alert").text, default=False)
