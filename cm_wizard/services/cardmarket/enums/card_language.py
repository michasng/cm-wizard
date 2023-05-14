from dataclasses import dataclass
from enum import Enum

from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage


@dataclass
class _CardLanguage:
    id: int
    labels: dict[CardmarketLanguage, str]


class CardLanguage(Enum):
    ENGLISH = _CardLanguage(
        1,
        {
            CardmarketLanguage.ENGLISH: "English",
            CardmarketLanguage.FRENCH: "Anglais",
            CardmarketLanguage.GERMAN: "Englisch",
            CardmarketLanguage.SPANISH: "Inglés",
            CardmarketLanguage.ITALIAN: "Inglese",
        },
    )
    FRENCH = _CardLanguage(
        2,
        {
            CardmarketLanguage.ENGLISH: "French",
            CardmarketLanguage.FRENCH: "Français",
            CardmarketLanguage.GERMAN: "Französisch",
            CardmarketLanguage.SPANISH: "Francés",
            CardmarketLanguage.ITALIAN: "Francese",
        },
    )
    GERMAN = _CardLanguage(
        3,
        {
            CardmarketLanguage.ENGLISH: "German",
            CardmarketLanguage.FRENCH: "Allemand",
            CardmarketLanguage.GERMAN: "Deutsch",
            CardmarketLanguage.SPANISH: "Alemán",
            CardmarketLanguage.ITALIAN: "Tedesco",
        },
    )
    SPANISH = _CardLanguage(
        4,
        {
            CardmarketLanguage.ENGLISH: "Spanish",
            CardmarketLanguage.FRENCH: "Espagnol",
            CardmarketLanguage.GERMAN: "Spanisch",
            CardmarketLanguage.SPANISH: "Español",
            CardmarketLanguage.ITALIAN: "Spagnolo",
        },
    )
    ITALIAN = _CardLanguage(
        5,
        {
            CardmarketLanguage.ENGLISH: "Italian",
            CardmarketLanguage.FRENCH: "Italien",
            CardmarketLanguage.GERMAN: "Italienisch",
            CardmarketLanguage.SPANISH: "Italiano",
            CardmarketLanguage.ITALIAN: "Italiano",
        },
    )
    SIMPLIFIED_CHINESE = _CardLanguage(
        6,
        {
            CardmarketLanguage.ENGLISH: "S-Chinese",
            CardmarketLanguage.FRENCH: "Chinois-S",
            CardmarketLanguage.GERMAN: "S-Chinesisch",
            CardmarketLanguage.SPANISH: "Chino-S",
            CardmarketLanguage.ITALIAN: "Cinese-S",
        },
    )
    JAPANESE = _CardLanguage(
        7,
        {
            CardmarketLanguage.ENGLISH: "Japanese",
            CardmarketLanguage.FRENCH: "Japonais",
            CardmarketLanguage.GERMAN: "Japanisch",
            CardmarketLanguage.SPANISH: "Japonés",
            CardmarketLanguage.ITALIAN: "Giapponese",
        },
    )
    PORTUGUESE = _CardLanguage(
        8,
        {
            CardmarketLanguage.ENGLISH: "Portuguese",
            CardmarketLanguage.FRENCH: "Portugais",
            CardmarketLanguage.GERMAN: "Portugiesisch",
            CardmarketLanguage.SPANISH: "Portugués",
            CardmarketLanguage.ITALIAN: "Portoghese",
        },
    )
    KOREAN = _CardLanguage(
        9,
        {
            CardmarketLanguage.ENGLISH: "Korean",
            CardmarketLanguage.FRENCH: "Coréen",
            CardmarketLanguage.GERMAN: "Koreanisch",
            CardmarketLanguage.SPANISH: "Coreano",
            CardmarketLanguage.ITALIAN: "Coreano",
        },
    )
    TRADITIONAL_CHINESE = _CardLanguage(
        10,
        {
            CardmarketLanguage.ENGLISH: "T-Chinese",
            CardmarketLanguage.FRENCH: "Chinois-T",
            CardmarketLanguage.GERMAN: "T-Chinesisch",
            CardmarketLanguage.SPANISH: "Chino-T",
            CardmarketLanguage.ITALIAN: "Cinese-T",
        },
    )

    @property
    def value(self) -> _CardLanguage:
        return super().value

    @classmethod
    def find_by_label(
        cls, cardmarket_language: CardmarketLanguage, label: str
    ) -> "CardLanguage":
        for card_language in CardLanguage:
            if card_language.value.labels[cardmarket_language] == label:
                return card_language
        raise NotImplementedError(
            f"Card language {label} is not supported in cardmarket language {cardmarket_language}."
        )
