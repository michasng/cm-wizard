from dataclasses import dataclass

from cm_wizard.services.cardmarket.model.card_condition import CardCondition
from cm_wizard.services.cardmarket.model.card_language import CardLanguage


@dataclass
class CardOfferSeller:
    name: str
    rating: str | None
    sale_count: int
    item_count: int
    eta_days: int | None
    eta_country_days: int
    location: str


@dataclass
class CardOfferProduct:
    expansions: str
    rarity: str
    condition: CardCondition
    language: CardLanguage
    is_reverse_holo: bool
    is_signed: bool
    is_first_edition: bool
    is_altered: bool
    image_url: str | None


@dataclass
class CardOffer:
    image_url: str
    seller: CardOfferSeller
    product: CardOfferProduct | None
    price_euro_cents: int
    amount: int


@dataclass
class CardOffers:
    name: str
    rules_text: str
    item_count: int
    version_count: int
    min_price_euro_cents: int
    price_trend_euro_cents: int
    offers: list[CardOffer]
