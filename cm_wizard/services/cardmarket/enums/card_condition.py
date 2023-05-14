from dataclasses import dataclass
from enum import Enum


@dataclass
class _CardCondition:
    id: int
    name: str
    abbreviation: str


class CardCondition(Enum):
    MINT = _CardCondition(1, "Mint", "MT")
    NEAR_MINT = _CardCondition(2, "Near Mint", "NM")
    EXCELLENT = _CardCondition(3, "Excellent", "EX")
    GOOD = _CardCondition(4, "Good", "GD")
    LIGHT_PLAYED = _CardCondition(5, "Light Played", "LP")
    PLAYED = _CardCondition(6, "Played", "PL")
    POOR = _CardCondition(7, "Poor", "PO")

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
