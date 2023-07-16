from cm_wizard.services.wizard_orchestrator_service import (
    CardOffer,
    CardOfferSeller,
    wizard_orchestrator_service,
)


def test__convert_to_sellers_offers():
    cards_offers = {
        "card 1": [
            CardOffer(
                price_euro_cents=1,
                quantity=1,
                seller=CardOfferSeller(id="seller 1"),
            ),
            CardOffer(
                price_euro_cents=2,
                quantity=1,
                seller=CardOfferSeller(id="seller 1"),
            ),
            CardOffer(
                price_euro_cents=2,
                quantity=3,
                seller=CardOfferSeller(id="seller 2"),
            ),
        ],
        "card 2": [
            CardOffer(
                price_euro_cents=3,
                quantity=2,
                seller=CardOfferSeller(id="seller 1"),
            ),
        ],
    }

    result = wizard_orchestrator_service._convert_to_sellers_offers(cards_offers)

    assert result == {
        "seller 1": {
            "card 1": [1, 2],
            "card 2": [3, 3],
        },
        "seller 2": {
            "card 1": [2, 2, 2],
        },
    }
