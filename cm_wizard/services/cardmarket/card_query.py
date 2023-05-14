from dataclasses import dataclass

from cm_wizard.services.cardmarket.enums.card_condition import CardCondition
from cm_wizard.services.cardmarket.enums.card_language import CardLanguage


@dataclass(frozen=True)
class CardQuery:
    id: str
    amount: int
    expansions: list[str] | None
    languages: list[CardLanguage] | None
    min_condition: CardCondition
    is_reverse_holo: bool | None
    is_signed: bool | None
    is_first_edition: bool | None
    is_altered: bool | None
