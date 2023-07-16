import bisect
import logging
import threading
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


class WizardOrchestratorService:
    def __init__(
        self,
        cardmarket_service: CardmarketService,
        shopping_wizard_service: ShoppingWizardService,
    ):
        self.cardmarket_service = cardmarket_service
        self.shopping_wizard_service = shopping_wizard_service
        self.stop_event = threading.Event()

    def _assert_not_stopped(self):
        if self.stop_event.is_set():
            raise InterruptedError("Wizard was stopped.")

    def _find_card_sellers(
        self,
        wants_items: list[WantsListPageItem],
        on_progress: OnProgressCallable,
    ) -> list[str]:
        current_progress: float = 0
        on_progress(current_progress, WizardOrchestratorStage.GET_CARDS_SELLERS)
        seller_ids: list[str] = []
        for item in wants_items:
            self._assert_not_stopped()
            card = self.cardmarket_service.get_card(item)
            current_progress += 1 / len(wants_items)
            on_progress(current_progress, WizardOrchestratorStage.GET_CARDS_SELLERS)

            if len(card.offers) == 0:
                _logger.warn(f"No offers found for card {card.name}.")
                continue

            _logger.debug(
                f'Lowest price for "{card.name}" is {format_price(card.offers[0].price_euro_cents)} cents by {card.offers[0].seller.id}.'
            )
            # TODO: Include more sellers depending on price and stats
            seller_ids.append(card.offers[0].seller.id)
        return seller_ids

    def _find_sellers_offers(
        self,
        wants_list_id: str,
        wants_ids: list[str],
        seller_ids: list[str],
        on_progress: OnProgressCallable,
    ) -> dict[str, dict[str, list[int]]]:
        current_progress: float = 0
        on_progress(current_progress, WizardOrchestratorStage.GET_SELLERS_OFFERS)
        sellers_offers: dict[str, dict[str, list[int]]] = {
            seller_id: {} for seller_id in seller_ids
        }
        for seller_id, seller_offers in sellers_offers.items():
            self._assert_not_stopped()
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
        wants_ids: list[str],
        wants_items: list[WantsListPageItem],
        sellers_offers: dict[str, dict[str, list[int]]],
        on_progress: OnProgressCallable,
    ) -> WizardOrchestratorResult:
        self._assert_not_stopped()
        on_progress(0, WizardOrchestratorStage.FIND_BEST_COMBINATION)
        result = shopping_wizard_service.find_best_offers(
            wants_ids, sellers_offers, constant_shipping_cost
        )

        @cache
        def get_item(card_id: str) -> WantsListPageItem:
            for item in wants_items:
                if item.id == card_id:
                    return item
            raise ValueError(f"Item {card_id} not found on wants list.")

        return WizardOrchestratorResult(
            total_price_euro_cents=result.total_price,
            missing_cards=result.missing_cards,
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
                for seller_id, seller_offers in result.sellers.items()
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
        wants_ids: list[str] = [item.id for item in wants_list_page.items]

        seller_ids = self._find_card_sellers(
            wants_items=wants_list_page.items,
            on_progress=on_progress,
        )

        sellers_offers = self._find_sellers_offers(
            wants_list_id=wants_list_id,
            wants_ids=wants_ids,
            seller_ids=seller_ids,
            on_progress=on_progress,
        )

        return self._find_best_combination(
            wants_ids=wants_ids,
            wants_items=wants_list_page.items,
            sellers_offers=sellers_offers,
            on_progress=on_progress,
        )


wizard_orchestrator_service = WizardOrchestratorService(
    cardmarket_service,
    shopping_wizard_service,
)
