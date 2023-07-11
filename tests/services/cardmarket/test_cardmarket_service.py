import pytest

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.card_query import CardQuery
from cm_wizard.services.cardmarket.cardmarket_service import CardmarketService
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service as cs
from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage
from cm_wizard.services.cardmarket.enums.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage


@pytest.fixture
def cardmarket_service() -> CardmarketService:
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


def test_get_wants_lists(requests_mock, cardmarket_service: CardmarketService):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Wants",
        text=file_text_contents("responses/en_Yugioh_Wants.html"),
    )

    result = cardmarket_service.get_wants_lists()

    assert len(result.items) == 30
    item = result.items[0]
    assert item.id == "15628908"
    assert item.title == "Adrian Gecko"
    assert item.distinct_cards_count == 25
    assert item.cards_count == 26
    assert (
        item.image_url
        == "https://product-images.s3.cardmarket.com/5/SDMM/110687/110687.jpg"
    )


def test_get_wants_list(requests_mock, cardmarket_service: CardmarketService):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Wants/15628908",
        text=file_text_contents("responses/en_Yugioh_Wants_15628908.html"),
    )

    result = cardmarket_service.get_wants_list("15628908")

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


def test_get_card(requests_mock, cardmarket_service: CardmarketService):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Cards/A-Feather-of-the-Phoenix?language=1,3&minCondition=1&isFirstEd=Y&isAltered=N",
        text=file_text_contents(
            "responses/en_Yugioh_Cards_A-Feather-of-the-Phoenix.html"
        ),
    )

    query = CardQuery(
        id="A-Feather-of-the-Phoenix",
        expansions=None,
        languages=[CardLanguage.ENGLISH, CardLanguage.GERMAN],
        min_condition=CardCondition.MINT,
        is_reverse_holo=None,
        is_signed=None,
        is_first_edition=True,
        is_altered=False,
    )
    result = cardmarket_service.get_card(query)

    assert result.name == "A Feather of the Phoenix"
    assert (
        result.rules_text
        == "Discard 1 card, then target 1 card in your GY; return that target to the top of your Deck."
    )
    assert result.item_count == 4285
    assert result.version_count == 7
    assert result.min_price_euro_cents == 2
    assert result.price_trend_euro_cents == 14
    assert len(result.offers) == 10
    offer = result.offers[0]
    assert (
        offer.image_url
        == "https://static.cardmarket.com/img/f7771ab8d3e18816866f63d3d07becfd/items/5/LEHD/364705.jpg"
    )
    assert offer.price_euro_cents == 2
    assert offer.amount == 1
    seller = offer.seller
    assert seller.id == "wkleebe1"
    assert seller.rating == "very-good"
    assert seller.sale_count == 45
    assert seller.item_count == 80
    assert seller.eta_days == 4
    assert seller.eta_country_days == 3
    assert seller.country == "Germany"
    product = offer.product
    assert product.expansion == "LEHD"
    assert product.rarity == "Common"
    assert product.condition == CardCondition.MINT
    assert product.language == CardLanguage.GERMAN
    assert product.is_reverse_holo == False
    assert product.is_signed == False
    assert product.is_first_edition == False
    assert product.is_altered == False
    assert product.image_url == None


def test_get_seller_wanted_offers(requests_mock, cardmarket_service: CardmarketService):
    requests_mock.get(
        "https://www.cardmarket.com/en/YuGiOh/Users/wkleebe1/Offers/Singles?idWantsList=15628908",
        text=file_text_contents(
            "responses/en_Yugioh_Users_wkleebe1_Offers_Singles_idWantsList_15628908.html"
        ),
    )

    result = cardmarket_service.get_seller_wanted_offers("wkleebe1", "15628908")

    assert result.id == "wkleebe1"
    assert result.country == "Germany"
    assert result.eta_days == 4
    assert result.total_count == 1
    assert result.current_page == 1
    assert result.total_page_count == 1

    assert len(result.offers) == 1
    offer = result.offers[0]
    assert (
        offer.image_url
        == "https://static.cardmarket.com/img/f7771ab8d3e18816866f63d3d07becfd/items/5/LEHD/364705.jpg"
    )
    assert offer.id == "A-Feather-of-the-Phoenix"
    assert offer.name == "A Feather of the Phoenix"
    assert offer.price_euro_cents == 2
    assert offer.quantity == 1
    product = offer.product
    assert product.expansion == "LEHD"
    assert product.rarity == "Common"
    assert product.condition == CardCondition.MINT
    assert product.language == CardLanguage.GERMAN
    assert product.is_reverse_holo == False
    assert product.is_signed == False
    assert product.is_first_edition == False
    assert product.is_altered == False
    assert product.image_url == None
