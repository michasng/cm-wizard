import logging
from dataclasses import dataclass

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


@dataclass
class RequestSeller:
    id: str
    offers: dict[str, list[int]]


@dataclass
class ResultSeller:
    id: str
    offers: list[tuple[str, int]]


class ShoppingWizardService:
    # TODO: Actually find the best combination, instead of returning the first one
    def find_best_offers(
        self, wants: list[str], sellers: list[RequestSeller]
    ) -> list[ResultSeller]:
        offers_to_buy: dict[str, list[tuple[str, int]]] = {
            seller.id: [] for seller in sellers
        }

        for card_id in wants:
            sellers_with_card = [
                seller for seller in sellers if card_id in seller.offers
            ]
            if len(sellers_with_card) == 0:
                continue
            seller = sellers_with_card[0]
            offers_to_buy[seller.id].append((card_id, seller.offers[card_id][0]))

        return [
            ResultSeller(id=key, offers=value) for key, value in offers_to_buy.items()
        ]


shopping_wizard_service = ShoppingWizardService()
