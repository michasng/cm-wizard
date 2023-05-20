from cm_wizard.services.shopping_wizard_service import (
    RequestSeller,
    ResultSeller,
    shopping_wizard_service,
)


def test_find_best_offers():
    wants = ["c1", "c2", "c3"]
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

    result = shopping_wizard_service.find_best_offers(wants, sellers)

    assert result == [
        ResultSeller(id="s1", offers=[("c1", 1), ("c2", 2), ("c3", 3)]),
        ResultSeller(id="s2", offers=[]),
        ResultSeller(id="s3", offers=[]),
    ]
