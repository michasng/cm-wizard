from typing import Generic, TypeVar

from bs4 import BeautifulSoup, Tag

from cm_wizard.services.locale import Locale


class HtmlElement:
    def __init__(self, tag: Tag, locale: Locale):
        self._tag = tag
        self._locale = locale


class HtmlPageElement(HtmlElement):
    def __init__(self, page_text: str, locale: Locale):
        super().__init__(BeautifulSoup(page_text, "html.parser"), locale)


T = TypeVar("T", bound=HtmlElement)


class HtmlChildElement(HtmlElement, Generic[T]):
    def __init__(self, parent: T, tag: Tag, locale: Locale):
        super().__init__(tag, locale)
        self._parent = parent
