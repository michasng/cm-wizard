import logging
from dataclasses import dataclass
from typing import Any, Iterator, TypeVar

import numpy as np

from cm_wizard.services.currency import format_price

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


@dataclass
class WizardResult:
    total_price: int
    sellers: dict[str, list[tuple[str, int]]]


T = TypeVar("T")


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


class ShoppingWizardService:
    # TODO: handle shipping costs
    def find_best_offers(
        self,
        wanted_cards: list[str],
        sellers: dict[str, dict[str, list[int]]],
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

        purchase_type = tuple[str, str]
        purchase_history_type = list[purchase_type]

        # + 1 row to check the previous card without a conditional
        price_table: np.ndarray[Any, np.dtype[np.int_]] = np.full(
            (len(wanted_cards) + 1, len(sellers)),
            np.iinfo(np.int32).max,
        )
        price_table[0][0] = 0  # initial price
        # numpy type hints suck right now. This is a matrix of purchase_history_type.
        purchase_history_table: np.ndarray = np.empty(
            (len(wanted_cards) + 1, len(sellers)),
            dtype=object,
        )
        purchase_history_table.fill([])

        def get_best_seller_index(card_index: int) -> np.signedinteger:
            card_prices: list[int] = price_table[card_index]
            return np.argmin(card_prices)

        for prev_card_index, card_id in enumerate(wanted_cards):
            card_index = prev_card_index + 1
            best_seller_index = get_best_seller_index(prev_card_index)
            previous_best_card_price = price_table[prev_card_index][best_seller_index]
            purchase_history = purchase_history_table[prev_card_index][
                best_seller_index
            ]
            for seller_index, (seller_id, seller_offers) in enumerate(sellers.items()):
                if card_id not in seller_offers:
                    continue  # seller does not offer the card

                purchase = (seller_id, card_id)
                purchase_count = purchase_history.count(purchase)
                if len(seller_offers[card_id]) <= purchase_count:
                    continue  # seller does not offer the card often enough

                seller_offer = seller_offers[card_id][purchase_count]
                price = previous_best_card_price + seller_offer
                price_table[card_index][seller_index] = price
                purchase_history_table[card_index][seller_index] = purchase_history + [
                    purchase
                ]

        best_seller_index = get_best_seller_index(-1)
        best_price = price_table[-1][best_seller_index]
        _logger.info(f"best total price: {format_price(best_price)}")

        best_purchase_history: purchase_history_type = purchase_history_table[-1][
            best_seller_index
        ]
        for seller_id, card_id in unique(best_purchase_history):
            purchase = (seller_id, card_id)
            count = best_purchase_history.count(purchase)
            for i in range(count):
                result_sellers[seller_id].append(
                    (card_id, sellers[seller_id][card_id][i])
                )

        return WizardResult(
            total_price=best_price,
            sellers={
                id: offers for id, offers in result_sellers.items() if len(offers) > 0
            },
        )


shopping_wizard_service = ShoppingWizardService()
