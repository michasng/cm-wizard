import re
from functools import cached_property
from typing import Callable

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage
from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.pages.helpers import extract_tooltip_image_url
from cm_wizard.services.cardmarket.pages.html_element import (
    HtmlChildElement,
    HtmlElement,
)


class CardProductInfo(HtmlChildElement[HtmlElement]):
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
