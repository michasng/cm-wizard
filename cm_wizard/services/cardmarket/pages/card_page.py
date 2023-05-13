import logging
import re
from functools import cached_property

from bs4 import ResultSet, Tag

from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage
from cm_wizard.services.cardmarket.pages.helpers import (
    extract_tooltip_image_url,
    parse_euro_cents,
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
        return self.tag.find(id="info").find(class_="infoContainer")

    @cached_property
    def _card_infos_dl_dd(self) -> ResultSet[Tag]:
        return self._card_infos.find(class_="labeled").find_all("dd")

    @cached_property
    def name(self) -> str:
        return self.tag.find("h1").text

    @cached_property
    def rules_text(self) -> str:
        return self._card_infos.find("div").text

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
        table = self.tag.find(id="table")
        rows: ResultSet[Tag] = table.find(class_="table-body").find_all(
            class_="article-row"
        )
        _logger.info(f"{len(rows)} offers found.")
        return [CardPageOffer(self, row) for row in rows]


class CardPageOffer(HtmlChildElement[CardPage]):
    @cached_property
    def image_url(self) -> str:
        return extract_tooltip_image_url(self.tag.find(class_="col-icon"))

    @cached_property
    def seller(self) -> "CardPageOfferSeller":
        seller_column = self.tag.find(class_="col-seller")
        return CardPageOfferSeller(self, seller_column)

    @cached_property
    def product(self) -> "CardPageOfferProduct":
        product_column = self.tag.find(class_="col-product")
        return CardPageOfferProduct(self, product_column)

    @cached_property
    def _offer_column(self) -> Tag:
        return self.tag.find(class_="col-offer")

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
        return self.tag.find(class_="seller-name")

    @cached_property
    def name(self) -> str:
        return self._seller_col_name.find("a").text

    @cached_property
    def _seller_ext_tooltips(self) -> ResultSet[Tag]:
        seller_col_ext = self.tag.find(class_="seller-extended")
        return seller_col_ext.find_all(attrs={"data-toggle": "tooltip"})

    @cached_property
    def rating(self) -> str | None:
        tooltip_classes = " ".join(self._seller_ext_tooltips[0]["class"])
        rating_match = re.search(
            r"fonticon-seller-rating-(?P<rating>\w+)",
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
    def expansions(self) -> str:
        raise NotImplementedError()

    @cached_property
    def rarity(self) -> str:
        raise NotImplementedError()

    @cached_property
    def condition(self) -> CardCondition:
        raise NotImplementedError()

    @cached_property
    def language(self) -> CardLanguage:
        raise NotImplementedError()

    @cached_property
    def is_reverse_holo(self) -> bool:
        raise NotImplementedError()

    @cached_property
    def is_signed(self) -> bool:
        raise NotImplementedError()

    @cached_property
    def is_first_edition(self) -> bool:
        raise NotImplementedError()

    @cached_property
    def is_altered(self) -> bool:
        raise NotImplementedError()

    @cached_property
    def image_url(self) -> str | None:
        raise NotImplementedError()
