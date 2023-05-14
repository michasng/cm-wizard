from dataclasses import dataclass
from enum import Enum


@dataclass
class _CardCondition:
    name: str
    abbreviation: str


class CardCondition(Enum):
    MINT = _CardCondition("Mint", "MT")
    NEAR_MINT = _CardCondition("Near Mint", "NM")
    EXCELLENT = _CardCondition("Excellent", "EX")
    GOOD = _CardCondition("Good", "GD")
    LIGHT_PLAYED = _CardCondition("Light Played", "LP")
    PLAYED = _CardCondition("Played", "PL")
    POOR = _CardCondition("Poor", "PO")

    @property
    def value(self) -> _CardCondition:
        return super().value

    @classmethod
    def find_by_abbreviation(cls, abbreviation: str) -> "CardCondition":
        for card_language in CardCondition:
            if card_language.value.abbreviation == abbreviation:
                return card_language
        raise NotImplementedError(
            f"Card condition abbreviation {abbreviation} is not supported."
        )
