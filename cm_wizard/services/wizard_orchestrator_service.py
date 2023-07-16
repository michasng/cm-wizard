import bisect
import logging
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache
from typing import Callable

from rapidfuzz import fuzz, process

from cm_wizard.services.cardmarket.cardmarket_service import (
    CardmarketService,
    cardmarket_service,
)
from cm_wizard.services.cardmarket.pages.wants_list_page import WantsListPageItem
from cm_wizard.services.currency import format_price
from cm_wizard.services.shopping_wizard_service import (
    ShoppingWizardService,
    WizardResult,
    shopping_wizard_service,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

constant_shipping_cost = 200  # rough estimate


class WizardOrchestratorStage(Enum):
    GET_WANTS_LIST = auto()
    GET_CARDS_SELLERS = auto()
    RANK_SELLERS = auto()
    GET_SELLERS_OFFERS = auto()
    FIND_BEST_COMBINATION = auto()


OnProgressCallable = Callable[[float, WizardOrchestratorStage], None]


@dataclass
class WizardOrchestratorResultOffer:
    card_id: str
    price_euro_cents: int
    # quantity: int # TODO: consolidate identical offers
    card_name: str
    image_url: str | None = None


@dataclass
class WizardOrchestratorResultSeller:
    id: str
    offers: list[WizardOrchestratorResultOffer]


@dataclass
class WizardOrchestratorResult:
    total_price_euro_cents: int
    missing_cards: list[str]
    sellers: list[WizardOrchestratorResultSeller]


@dataclass
class CardOfferSeller:
    id: str


@dataclass
class CardOffer:
    price_euro_cents: int
    quantity: int
    seller: CardOfferSeller


class WizardOrchestratorService:
    def __init__(
        self,
        cardmarket_service: CardmarketService,
        shopping_wizard_service: ShoppingWizardService,
    ):
        self.cardmarket_service = cardmarket_service
        self.shopping_wizard_service = shopping_wizard_service

    def _find_cards_offers(
        self,
        wants_items: list[WantsListPageItem],
        on_progress: OnProgressCallable,
    ) -> dict[str, list[CardOffer]]:
        current_progress: float = 0
        on_progress(current_progress, WizardOrchestratorStage.GET_CARDS_SELLERS)

        cards_offers: dict[str, list[CardOffer]] = {}
        for item in wants_items:
            card = self.cardmarket_service.get_card(item)
            current_progress += 1 / len(wants_items)
            on_progress(current_progress, WizardOrchestratorStage.GET_CARDS_SELLERS)

            if len(card.offers) == 0:
                _logger.warn(f"No offers found for card {card.name}.")
                continue

            _logger.debug(
                f'Lowest price for "{card.name}" is {format_price(card.offers[0].price_euro_cents)} cents by {card.offers[0].seller.id}.'
            )
            cards_offers[item.id] = card.offers
        return cards_offers

    def _convert_to_sellers_offers(
        self, cards_offers: dict[str, list[CardOffer]]
    ) -> dict[str, dict[str, list[int]]]:
        sellers_offers: dict[str, dict[str, list[int]]] = {}
        for card_id, offers in cards_offers.items():
            for offer in offers:
                if offer.seller.id not in sellers_offers:
                    sellers_offers[offer.seller.id] = {}
                seller_offer = sellers_offers[offer.seller.id]
                if card_id not in seller_offer:
                    seller_offer[card_id] = []
                seller_offer[card_id] += [offer.price_euro_cents] * offer.quantity
        return sellers_offers

    def _take_seller_ids_with_multiple_offers(
        self,
        sellers_offers: dict[str, dict[str, list[int]]],
    ) -> list[str]:
        return [
            seller_id for seller_id, offers in sellers_offers.items() if len(offers) > 1
        ]

    def _find_promising_sellers(
        self,
        wants_ids: set[str],
        cards_offers: dict[str, list[CardOffer]],
        on_progress: OnProgressCallable,
    ) -> set[str]:
        on_progress(0, WizardOrchestratorStage.RANK_SELLERS)

        incomplete_sellers_offers = self._convert_to_sellers_offers(
            cards_offers=cards_offers
        )
        preliminary_result = shopping_wizard_service.find_best_offers(
            wants_ids,
            incomplete_sellers_offers,
            constant_shipping_cost,
        )
        seller_ids = set(preliminary_result.sellers.keys())
        promising_seller_ids = self._take_seller_ids_with_multiple_offers(
            sellers_offers=incomplete_sellers_offers
        )
        seller_ids.update(promising_seller_ids)
        _logger.info(f"Considering offers from {len(seller_ids)} sellers.")
        return seller_ids

    def _find_sellers_offers(
        self,
        wants_list_id: str,
        wants_ids: set[str],
        seller_ids: set[str],
        on_progress: OnProgressCallable,
    ) -> dict[str, dict[str, list[int]]]:
        current_progress: float = 0
        on_progress(current_progress, WizardOrchestratorStage.GET_SELLERS_OFFERS)

        sellers_offers: dict[str, dict[str, list[int]]] = {
            seller_id: {} for seller_id in seller_ids
        }
        for seller_id, seller_offers in sellers_offers.items():
            # TODO: use pagination for more results
            seller_offers_page = self.cardmarket_service.get_seller_wanted_offers(
                seller_id=seller_id,
                wants_list_id=wants_list_id,
            )
            _logger.debug(
                f"Found {len(seller_offers_page.offers)} wanted offers from seller {seller_id}."
            )
            for offer in seller_offers_page.offers:
                card_id_match = process.extractOne(
                    offer.id, wants_ids, scorer=fuzz.WRatio
                )
                if card_id_match[1] < 100:
                    _logger.debug(
                        f"Closest card match for {offer.id} is {card_id_match}."
                    )
                card_id = card_id_match[0]

                if card_id not in seller_offers:
                    seller_offers[card_id] = []
                for _ in range(offer.quantity):
                    bisect.insort(seller_offers[card_id], offer.price_euro_cents)
            current_progress += 1 / len(sellers_offers)
            on_progress(current_progress, WizardOrchestratorStage.GET_SELLERS_OFFERS)
        return sellers_offers

    def _find_best_combination(
        self,
        wants_ids: set[str],
        sellers_offers: dict[str, dict[str, list[int]]],
        on_progress: OnProgressCallable,
    ) -> WizardResult:
        on_progress(0, WizardOrchestratorStage.FIND_BEST_COMBINATION)
        return shopping_wizard_service.find_best_offers(
            wants_ids,
            sellers_offers,
            constant_shipping_cost,
        )

    def _map_result(
        self,
        wizard_result: WizardResult,
        wants_items: list[WantsListPageItem],
    ) -> WizardOrchestratorResult:
        @cache
        def get_item(card_id: str) -> WantsListPageItem:
            return [item for item in wants_items if item.id == card_id][0]

        return WizardOrchestratorResult(
            total_price_euro_cents=wizard_result.total_price,
            missing_cards=wizard_result.missing_cards,
            sellers=[
                WizardOrchestratorResultSeller(
                    id=seller_id,
                    offers=[
                        WizardOrchestratorResultOffer(
                            card_id=card_id,
                            price_euro_cents=price,
                            card_name=(item := get_item(card_id)).name,
                            image_url=item.image_url,
                        )
                        for (card_id, price) in seller_offers
                    ],
                )
                for seller_id, seller_offers in wizard_result.sellers.items()
            ],
        )

    def run(
        self, wants_list_id: str, on_progress: OnProgressCallable
    ) -> WizardOrchestratorResult:
        wants_list_page = self.cardmarket_service.get_wants_list(wants_list_id)
        _logger.info(f"Running shopping wizard for {len(wants_list_page.items)} cards.")

        if len(wants_list_page.items) == 0:
            return WizardOrchestratorResult(
                total_price_euro_cents=0,
                missing_cards=[],
                sellers=[],
            )
        wants_ids: set[str] = {item.id for item in wants_list_page.items}

        cards_offers = self._find_cards_offers(
            wants_items=wants_list_page.items,
            on_progress=on_progress,
        )

        seller_ids = self._find_promising_sellers(
            wants_ids=wants_ids,
            cards_offers=cards_offers,
            on_progress=on_progress,
        )

        sellers_offers = self._find_sellers_offers(
            wants_list_id=wants_list_id,
            wants_ids=wants_ids,
            seller_ids=seller_ids,
            on_progress=on_progress,
        )

        wizard_result = self._find_best_combination(
            wants_ids=wants_ids,
            sellers_offers=sellers_offers,
            on_progress=on_progress,
        )

        return self._map_result(
            wizard_result=wizard_result,
            wants_items=wants_list_page.items,
        )


wizard_orchestrator_service = WizardOrchestratorService(
    cardmarket_service,
    shopping_wizard_service,
)
