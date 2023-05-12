from bs4 import BeautifulSoup, Tag


class Page:
    def __init__(self, html: BeautifulSoup):
        self.html = html


class PageTag:
    def __init__(self, page: Page, tag: Tag):
        self.page = page
        self.tag = tag
