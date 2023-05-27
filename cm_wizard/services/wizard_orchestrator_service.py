import bisect
import logging
from dataclasses import dataclass
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
    sellers: list[WizardOrchestratorResultSeller]


class WizardOrchestratorService:
    def __init__(
        self,
        cardmarket_service: CardmarketService,
        shopping_wizard_service: ShoppingWizardService,
    ):
        self.cardmarket_service = cardmarket_service
        self.shopping_wizard_service = shopping_wizard_service

    def run(
        self, wants_list_id: str, on_progress: Callable[[float], None]
    ) -> WizardOrchestratorResult:
        current_progress: float = 0.0

        def progress_by(additional_progress: float):
            nonlocal current_progress
            current_progress += additional_progress
            on_progress(current_progress)

        wants_list_page = self.cardmarket_service.get_wants_list(wants_list_id)
        _logger.info(f"Running shopping wizard for {len(wants_list_page.items)} cards.")
        progress_by(0.1)

        if len(wants_list_page.items) == 0:
            on_progress(1)
            return WizardOrchestratorResult(
                total_price_euro_cents=0,
                sellers=[],
            )

        sellers: dict[str, dict[str, list[int]]] = {}
        wanted_cards: list[str] = []
        get_card_progress = 0.3 / len(wants_list_page.items)
        for item in wants_list_page.items:
            card = self.cardmarket_service.get_card(item)

            if len(card.offers) == 0:
                _logger.warn(f"No offers found for card {card.name}.")
                progress_by(get_card_progress)
                continue

            _logger.debug(
                f'Lowest price for "{card.name}" is {format_price(card.offers[0].price_euro_cents)} cents by {card.offers[0].seller.id}.'
            )
            wanted_cards.append(item.id)
            # TODO: Include more sellers depending on price and stats
            sellers[card.offers[0].seller.id] = {}
            progress_by(get_card_progress)

        # current_progress is now at 0.4

        get_seller_wanted_offers_progress = 0.4 / len(wants_list_page.items)
        for seller_id, seller_offers in sellers.items():
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
                    offer.id, wanted_cards, scorer=fuzz.WRatio
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
            progress_by(get_seller_wanted_offers_progress)

        # current_progress is now at 0.8

        result = shopping_wizard_service.find_best_offers(wanted_cards, sellers)
        progress_by(0.2)

        @cache
        def get_item(card_id: str) -> WantsListPageItem:
            for item in wants_list_page.items:
                if item.id == card_id:
                    return item
            raise ValueError(f"Item {card_id} not found on wants list.")

        return WizardOrchestratorResult(
            total_price_euro_cents=result.total_price,
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


wizard_orchestrator_service = WizardOrchestratorService(
    cardmarket_service,
    shopping_wizard_service,
)
