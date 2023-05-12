import logging
import re
from http.cookiejar import CookieJar
from typing import Callable, TypeVar

import browser_cookie3
import requests
from bs4 import BeautifulSoup, Tag

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.pages.card_page import CardPage
from cm_wizard.services.cardmarket.pages.wants_list_page import (
    WantsListPage,
    WantsListPageItem,
)
from cm_wizard.services.cardmarket.pages.wants_lists_page import WantsListsPage

CARDMARKET_COOKIE_DOMAIN = ".cardmarket.com"
CARDMARKET_BASE_URL = f"https://www{CARDMARKET_COOKIE_DOMAIN}"

T = TypeVar("T")


class CardmarketException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class CardmarketService:
    _session: requests.Session | None = None
    _language: CardmarketLanguage
    _game: CardmarketGame

    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)

    def _cardmarket_url(self) -> str:
        return f"{CARDMARKET_BASE_URL}/{self._language.value}/{self._game.value}"

    def get_language(self) -> CardmarketLanguage:
        return self._language

    def get_game(self) -> CardmarketGame:
        return self._game

    def login(
        self,
        username: str,
        password: str,
        browser: Browser,
        user_agent: str,
        language: CardmarketLanguage = CardmarketLanguage.ENGLISH,
        game: CardmarketGame = CardmarketGame.YU_GI_OH,
    ):
        self._logger.info("login")

        session = self._open_new_session(browser, user_agent, language, game)

        login_page_response = session.get(f"{CARDMARKET_BASE_URL}/Login")
        if login_page_response.status_code != 200:
            self._logger.error(
                f"Failed to request login page with status {login_page_response.status_code}."
            )
            if login_page_response.status_code == 403:
                raise CardmarketException(
                    f"Login failed, please open cardmarket.com in {browser.value}."
                )
            self._log_to_file("login_page_response.html", login_page_response.text)
            raise CardmarketException(
                "Unexpected page error. Check login_page_response.html."
            )

        token_match = re.search(
            r'name="__cmtkn" value="(?P<token>\w+)"', login_page_response.text
        )
        if token_match is None or token_match.lastindex is None:
            self._logger.error("Token not found.")
            self._log_to_file("login_page_response.html", login_page_response.text)
            raise CardmarketException("No token found. Check login_page_response.html.")
        token = token_match.group("token")

        login_response = session.post(
            f"{self._cardmarket_url()}/PostGetAction/User_Login",
            data={
                "__cmtkn": token,
                "referalPage": f"/{language.value}/{game.value}",
                # credentials are only used here, in the login request
                "username": username,
                "userPassword": password,
            },
        )
        if login_response.status_code != 200:
            self._logger.error(
                f"Login request failed with status {login_response.status_code}."
            )
            self._log_to_file("login_response.txt", login_response.text)
            raise CardmarketException(
                "Unexpected login error. Check login_response.txt."
            )

        login_html = BeautifulSoup(login_response.text, "html.parser")
        error_message_container = login_html.find("h4", class_="alert-heading")
        if error_message_container:
            error_message = error_message_container.get_text(separator=". ") + "."
            self._logger.error(f"Login error response with message: {error_message}")
            raise CardmarketException(error_message)

        self._logger.info("Login successful.")

    def logout(self):
        self._logger.info("logout")
        self._close_session()

    def find_wants_lists(self) -> WantsListsPage:
        return self._get_authenticated_page(
            "wants lists",
            f"{self._cardmarket_url()}/Wants",
            lambda html: WantsListsPage(html, self.get_language()),
        )

    def find_wants_list(self, wants_list_id: str) -> WantsListPage:
        return self._get_authenticated_page(
            f"wants {wants_list_id}",
            f"{self._cardmarket_url()}/Wants/{wants_list_id}",
            lambda html: WantsListPage(html, self.get_language()),
        )

    def find_card_offers(self, wants_list_item: WantsListPageItem):
        return self._get_authenticated_page(
            f"card offers {wants_list_item.id}",
            f"{self._cardmarket_url()}/Cards/{wants_list_item.id}",
            lambda html: CardPage(html, self.get_language()),
        )

    def _log_to_file(self, path: str, content: str):
        self._logger.info(f'Start logging to file "{path}".')
        with open(path, "w") as out:
            out.write(content)
        self._logger.info(f'Done logging to file "{path}".')

    def _get_authenticated_page(
        self, page_name: str, url: str, parse_callback: Callable[[BeautifulSoup], T]
    ) -> T:
        self._logger.info(f"find {page_name}")

        def log_page_error() -> CardmarketException:
            error_file_name = f"{page_name.replace(' ', '_')}_page_response.html"
            self._log_to_file(error_file_name, page_response.text)
            return CardmarketException(
                f"Unexpected page error. Check {error_file_name}."
            )

        session = self._get_session()
        page_response = session.get(url)
        if page_response.status_code != 200:
            self._logger.error(
                f"Failed to request {page_name} page with status {page_response.status_code}."
            )
            if page_response.status_code == 401:
                raise CardmarketException(
                    "Your session may have expired. Please re-login."
                )
            raise log_page_error()

        try:
            page_html = BeautifulSoup(page_response.text, "html.parser")
            return parse_callback(page_html)
        except Exception as e:
            self._logger.error(f"Failed to parse {page_name} page for error: {e}")
            raise log_page_error()

    def _request_authenticated_page(
        self, page_name: str, url: str
    ) -> requests.Response:
        session = self._get_session()
        page_response = session.get(url)
        if page_response.status_code != 200:
            self._logger.error(
                f"Failed to request {page_name} page with status {page_response.status_code}."
            )
            if page_response.status_code == 401:
                raise CardmarketException(
                    "Your session may have expired. Please re-login."
                )
            self._log_to_file(
                f"{page_name.replace(' ', '_')}_page_response.html", page_response.text
            )
            raise CardmarketException(
                f"Unexpected page error. Check {page_name}_page_response.html."
            )
        return page_response

    def _get_session(self) -> requests.Session:
        assert self._session is not None
        return self._session

    def _open_new_session(
        self,
        browser: Browser,
        user_agent: str,
        language: CardmarketLanguage,
        game: CardmarketGame,
    ) -> requests.Session:
        if self._session != None:
            self._close_session()

        self._session = requests.Session()
        self._language = language
        self._game = game

        self._session.headers.update(
            {
                "accept": "*/*",
                "accept-language": "*",
                "cache-control": "no-cache",
                "dnt": "1",  # do not track
                # The cookies are browser dependent, so we need to identify the browser.
                "User-Agent": user_agent,
            }
        )

        cookies = self._extract_cookies(browser)
        self._logger.debug(
            f"{len(cookies)} cookies extracted from browser {browser.value}."
        )
        self._session.cookies.clear()
        for cookie in cookies:
            self._session.cookies.set_cookie(cookie)

        self._logger.debug("New session opened.")
        return self._session

    def _close_session(self):
        if self._session:
            self._session.close()
            self._logger.debug("Session closed.")
        self._session = None
        self._language = None
        self._game = None

    def _extract_cookies(self, browser: Browser) -> CookieJar:
        match browser:
            case Browser.CHROME:
                return browser_cookie3.chrome(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case Browser.CHROMIUM:
                return browser_cookie3.chromium(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case Browser.FIREFOX:
                return browser_cookie3.firefox(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case Browser.EDGE:
                return browser_cookie3.edge(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case Browser.SAFARI:
                return browser_cookie3.safari(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case Browser.OPERA:
                return browser_cookie3.opera(domain_name=CARDMARKET_COOKIE_DOMAIN)
            case _:
                raise NotImplementedError(f"Browser {browser.value} is not supported.")


cardmarket_service = CardmarketService()
