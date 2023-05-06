import logging
import platform
import re
from http.cookiejar import CookieJar

import browser_cookie3
import requests
from bs4 import BeautifulSoup, ResultSet, Tag

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.model.wants_lists import WantsLists, WantsListsItem

CARDMARKET_COOKIE_DOMAIN = ".cardmarket.com"
CARDMARKET_BASE_URL = f"https://www{CARDMARKET_COOKIE_DOMAIN}"


class CardmarketException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class CardmarketService:
    _session: requests.Session = None
    _language: CardmarketLanguage
    _game: CardmarketGame

    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)

    def _cardmarket_url(self) -> str:
        return f"{CARDMARKET_BASE_URL}/{self._language.value}/{self._game.value}"

    def login(
        self,
        username: str,
        password: str,
        browser: Browser = Browser.EDGE,
        language: CardmarketLanguage = CardmarketLanguage.ENGLISH,
        game: CardmarketGame = CardmarketGame.YU_GI_OH,
    ):
        self._logger.info("login")

        self._open_new_session(browser, language, game)

        login_page_response = self._session.get(f"{CARDMARKET_BASE_URL}/Login")
        if login_page_response.status_code != 200:
            self._logger.error(
                f"Failed to request login page with status {login_page_response.status_code}."
            )
            if login_page_response.status_code == 403:
                raise CardmarketException(
                    f"Login failed, please open cardmarket.com in {browser.value}."
                )
            self._logger.debug(login_page_response.text)
            raise CardmarketException("Unexpected page error. Check the console logs.")

        token_match = re.search(
            r'name="__cmtkn" value="(?P<token>\w+)"', login_page_response.text
        )
        if token_match.lastindex is None:
            self._logger.error("Token not found.")
            self._logger.debug(login_page_response.text)
            raise CardmarketException("No token found. Check the console logs.")
        token = token_match.group("token")

        login_response = self._session.post(
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
            self._logger.debug(login_response.text)
            raise CardmarketException("Unexpected login error. Check the console logs.")

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

    def get_wants_lists(self) -> WantsLists:
        self._logger.info("get_wants_lists")

        wants_page_response = self._session.get(f"{self._cardmarket_url()}/Wants")
        if wants_page_response.status_code != 200:
            self._logger.error(
                f"Failed to request wants lists page with status {wants_page_response.status_code}."
            )
            if wants_page_response.status_code == 403:
                raise CardmarketException(
                    "Your session may have expired. Please re-login."
                )
            self._logger.debug(wants_page_response.text)
            raise CardmarketException("Unexpected page error. Check the console logs.")

        wants_page_html = BeautifulSoup(wants_page_response.text, "html.parser")
        cards_html: ResultSet[Tag] = wants_page_html.find_all(class_="card")
        self._logger.info(f"{len(cards_html)} wants lists found.")

        items: list[WantsListsItem] = []
        for card_html in cards_html:
            link_html = card_html.find(class_="card-link-img-top")
            id_match = re.search(r"(?P<id>\d+)$", link_html.attrs["href"])
            title_html = card_html.find(class_="card-title")
            subtitle_html = card_html.find(class_="card-subtitle")
            count_matches = re.findall(r"\d+", subtitle_html.text)
            image_html = card_html.find("img")

            items.append(
                WantsListsItem(
                    id=id_match.group("id"),
                    title=title_html.text,
                    distinct_cards_count=count_matches[0],
                    cards_count=count_matches[1],
                    image_url=f"https:{image_html.attrs['data-echo']}",
                )
            )

        return WantsLists(items=items)

    def _open_new_session(
        self,
        browser: Browser,
        language: CardmarketLanguage,
        game: CardmarketGame,
    ):
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
                "User-Agent": self._create_user_agent_header(browser),
            }
        )

        cookies = self._extract_cookies(browser)
        self._logger.debug(
            f"{len(cookies)} cookies extracted from browser {browser.value}."
        )
        self._session.cookies = cookies

        self._logger.debug("New session opened.")

    def _close_session(self):
        if self._session:
            self._session.close()
            self._logger.debug("Session closed.")
        self._session = None
        self._language = None
        self._game = None

    # The cookies are system and browser dependent. The user-agent is apparently compared against the cookies.
    def _create_user_agent_header(self, browser: Browser):
        system_info = {
            "Darwin": "Macintosh; Intel Mac OS X 10_15_7",
            "Windows": "Windows NT 10.0; Win64; x64",
            "Linux": "X11; Linux x86_64",
        }[platform.system()]

        match browser:
            case Browser.CHROME:
                return f"Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            case Browser.CHROMIUM:
                return f"Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            case Browser.FIREFOX:
                return f"Mozilla/5.0 ({system_info}; rv:109.0) Gecko/20100101 Firefox/109.0"
            case Browser.EDGE:
                return f"Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68"
            case Browser.SAFARI:
                return f"Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            case Browser.OPERA:
                return f"Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.4759.3"
            case _:
                raise NotImplementedError(f"Browser {browser.value} is not supported.")

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
