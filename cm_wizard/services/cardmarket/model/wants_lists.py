from dataclasses import dataclass


@dataclass
class WantsListsItem:
    id: str
    title: str
    distinct_cards_count: int
    cards_count: int
    image_url: str


@dataclass
class WantsLists:
    items: list[WantsListsItem]
