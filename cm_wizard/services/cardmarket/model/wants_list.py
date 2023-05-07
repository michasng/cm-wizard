from dataclasses import dataclass

from cm_wizard.services.cardmarket.model.card_condition import CardCondition
from cm_wizard.services.cardmarket.model.card_language import CardLanguage


@dataclass
class WantsListItem:
    id: str
    name: str
    amount: int
    image_url: str
    expansions: list[str] | None
    languages: list[CardLanguage] | None
    min_condition: CardCondition
    is_reverse_holo: bool | None
    is_signed: bool | None
    is_first_edition: bool | None
    is_altered: bool | None
    buy_price_euro_cents: int | None
    has_mail_alert: bool


@dataclass
class WantsList:
    title: str
    items: list[WantsListItem]
