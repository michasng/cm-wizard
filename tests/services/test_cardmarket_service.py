import pytest

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service as cs
from cm_wizard.services.cardmarket.model.card_condition import CardCondition
from cm_wizard.services.cardmarket.model.card_language import CardLanguage


@pytest.fixture
def cardmarket_service():
    cs._open_new_session(
        browser=Browser.CHROME,
        user_agent="Mozilla/5.0...",
        language=CardmarketLanguage.ENGLISH,
        game=CardmarketGame.YU_GI_OH,
    )
    return cs


def file_text_contents(path: str) -> str:
    with open(path) as f:
        return f.read()


def test_find_wants_lists(requests_mock, cardmarket_service):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Wants",
        text=file_text_contents("responses/en_Yugioh_Wants.html"),
    )

    result = cardmarket_service.find_wants_lists()

    assert len(result.items) == 30
    item = result.items[0]
    assert item.id == "15628908"
    assert item.title == "Adrian Gecko"
    assert item.distinct_cards_count == 25
    assert item.cards_count == 26
    assert (
        item.image_url
        == "https://static.cardmarket.com/img/eca9f85e09930a4a11a2508a841d777e/items/5/GLAS/102481.jpg"
    )


def test_find_wants_list(requests_mock, cardmarket_service):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Wants/15628908",
        text=file_text_contents("responses/en_Yugioh_Wants_15628908.html"),
    )

    result = cardmarket_service.find_wants_list("15628908")

    assert result.title == "Adrian Gecko"
    assert len(result.items) == 25
    item = result.items[0]
    assert item.id == "A-Feather-of-the-Phoenix"
    assert item.name == "A Feather of the Phoenix"
    assert item.amount == 1
    assert (
        item.image_url
        == "https://static.cardmarket.com/img/65a04d7575f14f5ee1170872e19d67f7/items/5/CP03/101806.jpg"
    )
    assert item.expansions == ["LCYW", "FET"]
    assert item.languages == [CardLanguage.ENGLISH, CardLanguage.GERMAN]
    assert item.min_condition == CardCondition.MINT
    assert item.is_reverse_holo == None
    assert item.is_signed == False
    assert item.is_first_edition == True
    assert item.is_altered == True
    assert item.buy_price_euro_cents == 100
    assert item.has_mail_alert == False
