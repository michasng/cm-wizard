from typing import Generic, TypeVar

from bs4 import BeautifulSoup, Tag

from cm_wizard.services.cardmarket.cardmarket_language import CardmarketLanguage


class HtmlElement:
    def __init__(self, tag: Tag):
        self.tag = tag


class HtmlPageElement(HtmlElement):
    def __init__(self, html: BeautifulSoup, language: CardmarketLanguage):
        super().__init__(html)
        self.language = language


T = TypeVar("T", bound=HtmlElement)


class HtmlChildElement(HtmlElement, Generic[T]):
    def __init__(self, parent: T, tag: Tag):
        super().__init__(tag)
        self.parent = parent
