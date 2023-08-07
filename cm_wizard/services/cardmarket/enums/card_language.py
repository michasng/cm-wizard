from enum import Enum

from cm_wizard.services.locale import Locale


class CardLanguage(Enum):
    ENGLISH = 1
    FRENCH = 2
    GERMAN = 3
    SPANISH = 4
    ITALIAN = 5
    SIMPLIFIED_CHINESE = 6
    JAPANESE = 7
    PORTUGUESE = 8
    KOREAN = 9
    TRADITIONAL_CHINESE = 10

    def get_label(self, locale: Locale) -> str:
        return locale.get_label(f"cardLanguages.{self.value}")

    @classmethod
    def find_by_label(cls, locale: Locale, label: str) -> "CardLanguage":
        for card_language in CardLanguage:
            if card_language.get_label(locale) == label:
                return card_language
        raise NotImplementedError(
            f'Card Language "{label}" was not found in locale {locale}.'
        )
