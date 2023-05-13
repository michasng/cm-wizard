import pytest

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service as cs


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
