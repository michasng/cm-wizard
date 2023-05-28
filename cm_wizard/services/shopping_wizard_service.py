import logging
from dataclasses import dataclass, field
from typing import Any, Iterator, TypeVar

import numpy as np

from cm_wizard.services.currency import format_price

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

T = TypeVar("T")
# use max int / 2, because otherwise max int + shipping may overflow
max_price = np.iinfo(np.int32).max / 2


@dataclass
class WizardResult:
    total_price: int
    sellers: dict[str, list[tuple[str, int]]]
    missing_cards: list[str] = field(default_factory=list)


def create_matrix(col_count: int, row_count: int, initial_value: T) -> list[list[T]]:
    return [[initial_value] * col_count] * row_count


def unique(lst: list[T]) -> Iterator[T]:
    """
    Returns an iterator with unique elements.
    Preserves the order of elements (in contrast to a set).
    """
    used = set()
    for e in lst:
        if e not in used:
            used.add(e)
            yield e


purchase_type = tuple[str, str]
purchase_history_type = list[purchase_type]


class ShoppingWizardService:
    # TODO: handle shipping costs
    def find_best_offers(
        self,
        wanted_cards: list[str],
        sellers: dict[str, dict[str, list[int]]],
        shipping_cost: int = 0,
    ) -> WizardResult:
        """
        Returns (one of) the best combinations of cards to buy from sellers
        in order to buy all wanted_cards.
        The wanted_cards may contain duplicates.
        The seller offers for each card must be sorted ascendingly by price.
        """

        result_sellers: dict[str, list[tuple[str, int]]] = {
            id: [] for id, _ in sellers.items()
        }
        missing_cards: list[str] = []

        # + 1 row to check the previous card without a conditional
        price_table: np.ndarray[Any, np.dtype[np.int_]] = np.full(
            (len(wanted_cards) + 1, len(sellers)),
            max_price,
        )
        price_table[0][0] = 0  # initial price
        # numpy type hints suck right now. This is a matrix of purchase_history_type.
        purchase_history_table: np.ndarray = np.empty(
            (len(wanted_cards) + 1, len(sellers)),
            dtype=object,
        )
        purchase_history_table.fill([])

        def additional_seller_shipping_cost(
            seller_id: str,
            purchase_history: purchase_history_type,
        ) -> int:
            purchases_with_seller = filter(
                lambda purchase: purchase[0] == seller_id, purchase_history
            )
            is_seller_in_history = any(purchases_with_seller)
            return 0 if is_seller_in_history else shipping_cost

        def get_best_seller_index(
            card_index: int, seller_id: str | None
        ) -> np.signedinteger:
            card_prices = price_table[card_index]
            if seller_id is None:
                return np.argmin(card_prices)

            histories = purchase_history_table[card_index]
            shipping_costs = np.array(
                [
                    additional_seller_shipping_cost(seller_id, history)
                    for history in histories
                ]
            )
            return np.argmin(card_prices + shipping_costs)

        def get_base_indices(
            prev_card_index: int, seller_id: str | None
        ) -> tuple[int, np.signedinteger]:
            base_card_index = prev_card_index
            while True:
                base_seller_index = get_best_seller_index(base_card_index, seller_id)
                if price_table[base_card_index][base_seller_index] != max_price:
                    return base_card_index, base_seller_index
                base_card_index -= 1

        for prev_card_index, card_id in enumerate(wanted_cards):
            card_index = prev_card_index + 1
            card_found = False
            for seller_index, (seller_id, seller_offers) in enumerate(sellers.items()):
                if card_id not in seller_offers:
                    continue  # seller does not offer the card

                (base_card_index, base_seller_index) = get_base_indices(
                    prev_card_index, seller_id
                )
                base_card_price = price_table[base_card_index][base_seller_index]
                base_purchase_history: purchase_history_type = purchase_history_table[
                    base_card_index
                ][base_seller_index]

                purchase = (seller_id, card_id)
                purchase_count = base_purchase_history.count(purchase)
                if len(seller_offers[card_id]) <= purchase_count:
                    continue  # seller does not offer the card often enough

                seller_offer = seller_offers[card_id][purchase_count]

                additional_shipping_cost = additional_seller_shipping_cost(
                    seller_id, base_purchase_history
                )
                price = base_card_price + seller_offer + additional_shipping_cost
                price_table[card_index][seller_index] = price
                purchase_history_table[card_index][
                    seller_index
                ] = base_purchase_history + [purchase]
                card_found = True
            if not card_found:
                missing_cards.append(card_id)

        (result_card_index, result_seller_index) = get_base_indices(-1, None)
        total_price = price_table[result_card_index][result_seller_index]
        purchase_history: purchase_history_type = purchase_history_table[
            result_card_index
        ][result_seller_index]

        for seller_id, card_id in unique(purchase_history):
            purchase = (seller_id, card_id)
            count = purchase_history.count(purchase)
            for i in range(count):
                result_sellers[seller_id].append(
                    (card_id, sellers[seller_id][card_id][i])
                )

        _logger.info(f"best total price: {format_price(total_price)}")
        return WizardResult(
            total_price=total_price,
            sellers={
                id: offers for id, offers in result_sellers.items() if len(offers) > 0
            },
            missing_cards=missing_cards,
        )


shopping_wizard_service = ShoppingWizardService()
