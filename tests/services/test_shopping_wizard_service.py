from cm_wizard.services.shopping_wizard_service import (
    RequestSeller,
    Result,
    shopping_wizard_service,
)


def test_find_best_offers_basic():
    wanted_cards = ["c1", "c2", "c3"]
    sellers = [
        RequestSeller(
            id="s1",
            offers={
                "c1": [1],
                "c2": [2],
                "c3": [3],
            },
        ),
        RequestSeller(
            id="s2",
            offers={
                "c1": [2],
                "c2": [1],
                "c3": [1],
            },
        ),
        RequestSeller(
            id="s3",
            offers={
                "c2": [2],
                "c3": [1],
            },
        ),
    ]

    result = shopping_wizard_service.find_best_offers(wanted_cards, sellers)

    assert result == Result(
        total_price=3,
        sellers={
            "s1": [("c1", 1)],
            "s2": [("c2", 1), ("c3", 1)],
            "s3": [],
        },
    )


def test_find_best_offers_duplicate_wants():
    wanted_cards = ["c1", "c2", "c2", "c3", "c3", "c3", "c3"]
    sellers = [
        RequestSeller(
            id="s1",
            offers={
                "c1": [1],
                "c2": [2],
                "c3": [3],
            },
        ),
        RequestSeller(
            id="s2",
            offers={
                "c1": [2],
                "c2": [1],
                "c3": [1],
            },
        ),
        RequestSeller(
            id="s3",
            offers={
                "c2": [2],
                "c3": [1, 2],
            },
        ),
    ]

    result = shopping_wizard_service.find_best_offers(wanted_cards, sellers)

    assert result == Result(
        total_price=11,
        sellers={
            "s1": [("c1", 1), ("c2", 2), ("c3", 3)],
            "s2": [("c2", 1), ("c3", 1)],
            "s3": [("c3", 1), ("c3", 2)],
        },
    )
