import logging
import re
from functools import cached_property
from typing import Callable

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage
from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.pages.helpers import (
    extract_tooltip_image_url,
    find_tooltip,
    parse_euro_cents,
    strip_multi_spaces,
)
from cm_wizard.services.cardmarket.pages.html_element import (
    HtmlChildElement,
    HtmlPageElement,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class CardPage(HtmlPageElement):
    @cached_property
    def _card_infos(self) -> Tag:
        return self._tag.find(id="info").find(class_="infoContainer")

    @cached_property
    def _card_infos_dl_dd(self) -> ResultSet[Tag]:
        return self._card_infos.find(class_="labeled").find_all("dd")

    @cached_property
    def name(self) -> str:
        return self._tag.find("h1").text

    @cached_property
    def rules_text(self) -> str:
        text = self._card_infos.find("div").get_text(strip=True)
        return strip_multi_spaces(text)

    @cached_property
    def item_count(self) -> int:
        return int(self._card_infos_dl_dd[0].text)

    @cached_property
    def version_count(self) -> int:
        return int(self._card_infos_dl_dd[1].text)

    @cached_property
    def min_price_euro_cents(self) -> int:
        return parse_euro_cents(self._card_infos_dl_dd[2].text)

    @cached_property
    def price_trend_euro_cents(self) -> int:
        return parse_euro_cents(self._card_infos_dl_dd[3].text)

    @cached_property
    def offers(self) -> list["CardPageOffer"]:
        table = self._tag.find(id="table")
        rows: ResultSet[Tag] = table.find(class_="table-body").find_all(
            class_="article-row"
        )
        _logger.info(f"{len(rows)} offers found.")
        return [CardPageOffer(self, row) for row in rows]


class CardPageOffer(HtmlChildElement[CardPage]):
    @cached_property
    def image_url(self) -> str:
        tooltip = find_tooltip(self._tag.find(class_="col-icon"))
        return extract_tooltip_image_url(tooltip)

    @cached_property
    def seller(self) -> "CardPageOfferSeller":
        seller_column = self._tag.find(class_="col-seller")
        return CardPageOfferSeller(self, seller_column)

    @cached_property
    def product(self) -> "CardPageOfferProduct":
        product_column = self._tag.find(class_="col-product")
        return CardPageOfferProduct(self, product_column)

    @cached_property
    def _offer_column(self) -> Tag:
        return self._tag.find(class_="col-offer")

    @cached_property
    def price_euro_cents(self) -> int:
        return parse_euro_cents(
            self._offer_column.find(class_="price-container").find("span").text
        )

    @cached_property
    def amount(self) -> int:
        return int(self._offer_column.find(class_="amount-container").find("span").text)


class CardPageOfferSeller(HtmlChildElement[CardPageOffer]):
    @cached_property
    def _seller_col_name(self) -> Tag:
        return self._tag.find(class_="seller-name")

    @cached_property
    def name(self) -> str:
        return self._seller_col_name.find("a").text

    @cached_property
    def _seller_ext_tooltips(self) -> ResultSet[Tag]:
        seller_col_ext = self._tag.find(class_="seller-extended")
        return seller_col_ext.find_all(attrs={"data-toggle": "tooltip"})

    @cached_property
    def rating(self) -> str | None:
        tooltip_classes = " ".join(self._seller_ext_tooltips[0]["class"])
        rating_match = re.search(
            r"fonticon-seller-rating-(?P<rating>[\w-]+)",
            tooltip_classes,
        )
        assert (
            rating_match is not None
        ), f'Rating not found in tooltip classes "{tooltip_classes}".'

        if rating_match.group("rating") == "none":
            return None

        return rating_match.group("rating")

    @cached_property
    def _sell_count_matches(self) -> list[str]:
        tooltip_title: str = self._seller_ext_tooltips[1].attrs["title"]
        sell_count_matches = re.findall(r"\d+", tooltip_title)
        assert (
            len(sell_count_matches) == 2
        ), f'Sale and item counts not found in tooltip title "{tooltip_title}".'
        return sell_count_matches

    @cached_property
    def sale_count(self) -> int:
        return int(self._sell_count_matches[0])

    @cached_property
    def item_count(self) -> int:
        return int(self._sell_count_matches[1])

    @cached_property
    def _eta_matches(self) -> list[int]:
        tooltip_title: str = self._seller_ext_tooltips[2].attrs["title"]
        eta_matches = re.findall(r":\s*(\d+)", tooltip_title)
        assert (
            len(eta_matches) > 0
        ), f'Eta not found in tooltip title "{tooltip_title}".'
        return [int(match) for match in eta_matches]

    @cached_property
    def eta_days(self) -> int | None:
        if len(self._eta_matches) == 1:
            return None
        return self._eta_matches[0]

    @cached_property
    def eta_country_days(self) -> int:
        return self._eta_matches[-1]

    @cached_property
    def location(self) -> str:
        tooltip_title = self._seller_col_name.find(
            attrs={"data-toggle": "tooltip"}
        ).attrs["title"]
        location_matches = re.findall(r":\s*(\w+)", tooltip_title)
        assert (
            len(location_matches) == 1
        ), f'Location not found in tooltip title "{tooltip_title}".'
        return location_matches[0]


class CardPageOfferProduct(HtmlChildElement[CardPageOffer]):
    @cached_property
    def _product_attributes(self) -> Tag:
        return self._tag.find(class_="product-attributes")

    @cached_property
    def _product_tooltips(self) -> ResultSet[Tag]:
        return self._product_attributes.find_all(attrs={"data-toggle": "tooltip"})

    def _find_product_tooltip(
        self, condition: Callable[[Tag], bool], error_key: str
    ) -> Tag | None:
        true_tooltips = list(filter(condition, self._product_tooltips))

        if len(true_tooltips) == 0:
            return None

        assert len(true_tooltips) == 1, f"Ambiguous {error_key} tooltip search."
        return true_tooltips[0]

    def _product_tooltip_bool(self, title: str) -> bool:
        def has_original_title(tooltip: Tag):
            return (
                "data-original-title" in tooltip.attrs
                and tooltip.attrs["data-original-title"] == "title"
            )

        tooltip = self._find_product_tooltip(has_original_title, title)
        return tooltip is not None

    @cached_property
    def expansion(self) -> str:
        return (
            self._product_attributes.find(class_="expansion-symbol").find("span").text
        )

    @cached_property
    def rarity(self) -> str | None:
        def is_rarity_tooltip(tooltip: Tag):
            return "style" in tooltip.attrs and "ssRarity" in tooltip.attrs["style"]

        tooltip = self._find_product_tooltip(is_rarity_tooltip, "rarity")

        if tooltip is None:
            return None

        return tooltip.attrs["title"]

    @cached_property
    def condition(self) -> CardCondition:
        abbreviation = (
            self._product_attributes.find(class_="article-condition").find("span").text
        )
        return CardCondition.find_by_abbreviation(abbreviation)

    @cached_property
    def language(self) -> CardLanguage:
        def is_language_tooltip(tooltip: Tag):
            return (
                "style" in tooltip.attrs
                and "ssMain2" in tooltip.attrs["style"]
                and re.search(
                    r"background-position: -\d+px -0px;", tooltip.attrs["style"]
                )
                is not None
            )

        tooltip = self._find_product_tooltip(is_language_tooltip, "language")
        assert tooltip is not None, "No card language found in tooltips."

        return CardLanguage.find_by_label(
            CardmarketLanguage.ENGLISH, tooltip.attrs["data-original-title"]
        )

    @cached_property
    def is_reverse_holo(self) -> bool:
        return self._product_tooltip_bool("Reverse Holo")

    @cached_property
    def is_signed(self) -> bool:
        return self._product_tooltip_bool("Signed")

    @cached_property
    def is_first_edition(self) -> bool:
        return self._product_tooltip_bool("First Edition")

    @cached_property
    def is_altered(self) -> bool:
        return self._product_tooltip_bool("Altered")

    @cached_property
    def image_url(self) -> str | None:
        tooltip = self._product_attributes.find(class_="fonticon-camera")
        if tooltip is None:
            return None
        return extract_tooltip_image_url(tooltip)
