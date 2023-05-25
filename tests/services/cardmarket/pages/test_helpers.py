from cm_wizard.services.cardmarket.pages.helpers import extract_card_id_from_url


def test_extract_card_id_from_url():
    assert (
        extract_card_id_from_url("/en/YuGiOh/Cards/A-Feather-of-the-Phoenix")
        == "A-Feather-of-the-Phoenix"
    )
    assert (
        extract_card_id_from_url(
            "/en/YuGiOh/Products/Singles/Legendary-Hero-Decks/A-Feather-of-the-Phoenix?language=1,3&amp;minCondition=5"
        )
        == "A-Feather-of-the-Phoenix"
    )
    assert (
        extract_card_id_from_url("Singles/a/Dragon-s-Fighting-Spirit-V-1")
        == "Dragon-s-Fighting-Spirit"
    )
    assert (
        extract_card_id_from_url("Singles/a/Dragon-s-Fighting-Spirit-V-2")
        == "Dragon-s-Fighting-Spirit"
    )
    assert (
        extract_card_id_from_url(
            "Singles/a/The-Flute-of-Summoning-Dragon-V2-Super-Rare"
        )
        == "The-Flute-of-Summoning-Dragon"
    )
    assert (
        extract_card_id_from_url("Singles/a/Cockroach-Knight-V1-Common")
        == "Cockroach-Knight"
    )
