import logging
from dataclasses import dataclass
from typing import Iterator, TypeVar

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# max int32, however python3 has no such limit
# other "infinities" like float("inf") or math.inf are of type float
infinity = 2147483647


@dataclass
class Result:
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
    ) -> Result:
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

        price_table: list[list[int]] = create_matrix(
            len(sellers), len(wanted_cards), infinity
        )
        purchase_history_table: list[list[purchase_history_type]] = create_matrix(
            len(sellers), len(wanted_cards), []
        )

        best_seller_index = -1
        for card_index, card_id in enumerate(wanted_cards):
            previous_best_card_price = (
                0 if card_index == 0 else price_table[card_index - 1][best_seller_index]
            )
            purchase_history: purchase_history_type = (
                []
                if card_index == 0
                else purchase_history_table[card_index - 1][best_seller_index]
            )
            best_card_price = infinity
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

                if price < best_card_price:
                    best_card_price = price
                    best_seller_index = seller_index

        best_price = price_table[-1][best_seller_index]
        _logger.info(f"best total price: {best_price}")

        best_purchase_history: list[purchase_type] = purchase_history_table[-1][
            best_seller_index
        ]
        for seller_id, card_id in unique(best_purchase_history):
            purchase = (seller_id, card_id)
            count = best_purchase_history.count(purchase)
            for i in range(count):
                result_sellers[seller_id].append(
                    (card_id, sellers[seller_id][card_id][i])
                )

        return Result(
            total_price=best_price,
            sellers=result_sellers,
        )


shopping_wizard_service = ShoppingWizardService()
