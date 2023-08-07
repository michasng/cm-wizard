from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage
from cm_wizard.services.locale import Locale


def test_get_label():
    test_labels = {
        CardmarketLanguage.ENGLISH: "Germany",
        CardmarketLanguage.FRENCH: "Allemagne",
        CardmarketLanguage.GERMAN: "Deutschland",
        CardmarketLanguage.SPANISH: "Alemania",
        CardmarketLanguage.ITALIAN: "Germania",
    }

    for language in CardmarketLanguage:
        locale = Locale(language)

        assert locale.get_label("locations.D") == test_labels[language]
