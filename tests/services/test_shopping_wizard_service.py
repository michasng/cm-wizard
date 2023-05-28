from cm_wizard.services.shopping_wizard_service import (
    WizardResult,
    shopping_wizard_service,
)


def test_find_best_offers_simple_case():
    wanted_cards = ["c1", "c2", "c3"]
    sellers = {
        "s1": {
            "c1": [1],
            "c2": [2],
            "c3": [3],
        },
        "s2": {
            "c1": [2],
            "c2": [1],
            "c3": [1],
        },
        "s3": {
            "c2": [2],
            "c3": [1],
        },
    }

    result = shopping_wizard_service.find_best_offers(wanted_cards, sellers)

    assert result == WizardResult(
        total_price=3,
        sellers={
            "s1": [("c1", 1)],
            "s2": [("c2", 1), ("c3", 1)],
        },
    )


def test_find_best_offers_with_duplicate_wants():
    wanted_cards = ["c1", "c2", "c2", "c3", "c3", "c3", "c3"]
    sellers = {
        "s1": {
            "c1": [1],
            "c2": [2],
            "c3": [3],
        },
        "s2": {
            "c1": [2],
            "c2": [1],
            "c3": [1],
        },
        "s3": {
            "c2": [2],
            "c3": [1, 2],
        },
    }

    result = shopping_wizard_service.find_best_offers(wanted_cards, sellers)

    assert result == WizardResult(
        total_price=11,
        sellers={
            "s1": [("c1", 1), ("c2", 2), ("c3", 3)],
            "s2": [("c2", 1), ("c3", 1)],
            "s3": [("c3", 1), ("c3", 2)],
        },
    )
