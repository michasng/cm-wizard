import logging
from dataclasses import dataclass

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# max int32, however python3 has no such limit
# other "infinities" like float("inf") or math.inf are of type float
infinity = 2147483647


@dataclass
class RequestSeller:
    id: str
    offers: dict[str, list[int]]


@dataclass
class ResultSeller:
    id: str
    offers: list[tuple[str, int]]


class ShoppingWizardService:
    # TODO: handle duplicates correctly
    # TODO: handle shipping costs
    def find_best_offers(
        self, wanted_cards: list[str], sellers: list[RequestSeller]
    ) -> list[ResultSeller]:
        """
        Returns one of the best combinations of cards to buy from sellers
        in order to buy all wanted_cards.
        The wanted_cards may contain duplicates.
        The seller offers for each card must be sorted ascendingly by price.
        """

        offers_to_buy: dict[str, list[tuple[str, int]]] = {
            seller.id: [] for seller in sellers
        }

        price_table: list[list[int]] = [[infinity] * len(sellers)] * len(wanted_cards)
        seller_history_table: list[list[list[int]]] = [[[]] * len(sellers)] * len(
            wanted_cards
        )

        best_seller_index = -1
        for card_index, card_id in enumerate(wanted_cards):
            previous_best_card_price = (
                0 if card_index == 0 else price_table[card_index - 1][best_seller_index]
            )
            seller_history = (
                []
                if card_index == 0
                else seller_history_table[card_index - 1][best_seller_index]
            )
            best_card_price = infinity
            for seller_index, seller in enumerate(sellers):
                if card_id not in seller.offers:
                    continue

                seller_offer = min(seller.offers[card_id])
                price = previous_best_card_price + seller_offer
                price_table[card_index][seller_index] = price
                seller_history_table[card_index][seller_index] = seller_history + [
                    seller_index
                ]

                if price < best_card_price:
                    best_card_price = price
                    best_seller_index = seller_index

        best_price = price_table[-1][best_seller_index]
        _logger.info(f"best total price: {best_price}")
        seller_history = seller_history_table[-1][best_seller_index]
        for card_index, card_id in enumerate(wanted_cards):
            seller_index = seller_history[card_index]
            seller = sellers[seller_index]
            offers_to_buy[seller.id].append((card_id, seller.offers[card_id][0]))

        return [
            ResultSeller(id=key, offers=value) for key, value in offers_to_buy.items()
        ]


shopping_wizard_service = ShoppingWizardService()
