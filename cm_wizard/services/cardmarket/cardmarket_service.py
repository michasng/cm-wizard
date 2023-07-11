import logging
import re
from http.cookiejar import CookieJar

import browser_cookie3
import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.card_query import CardQuery
from cm_wizard.services.cardmarket.enums.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage
from cm_wizard.services.cardmarket.log_retry import LogRetry
from cm_wizard.services.cardmarket.pages.card_page import CardPage
from cm_wizard.services.cardmarket.pages.seller_offers_page import SellerOffersPage
from cm_wizard.services.cardmarket.pages.wants_list_page import WantsListPage
from cm_wizard.services.cardmarket.pages.wants_lists_page import WantsListsPage

CARDMARKET_COOKIE_DOMAIN = ".cardmarket.com"
CARDMARKET_BASE_URL = f"https://www{CARDMARKET_COOKIE_DOMAIN}"
RATE_LIMIT_PERIOD_SECONDS: float = 1
RATE_LIMIT_CALL_COUNT: int = 1

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class CardmarketException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code


class CardmarketService:
    _session: requests.Session | None = None
    _language: CardmarketLanguage
    _game: CardmarketGame
    _rate_limited: bool = True

    def _cardmarket_url(self) -> str:
        return f"{CARDMARKET_BASE_URL}/{self._language.value}/{self._game.value}"

    @property
    def language(self) -> CardmarketLanguage:
        return self._language

    @property
    def game(self) -> CardmarketGame:
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
        _logger.info("login")

        session = self._open_new_session(browser, user_agent, language, game)

        login_page_response = session.get(f"{CARDMARKET_BASE_URL}/Login")
        if login_page_response.status_code != 200:
            _logger.error(
                f"Failed to request login page with status {login_page_response.status_code}."
            )
            if login_page_response.status_code == 403:
                raise CardmarketException(
                    f"Login failed, please open cardmarket.com in {browser.value}.",
                    status_code=403,
                )
            self._log_to_file("login_page_response.html", login_page_response.text)
            raise CardmarketException(
                "Unexpected page error. Check login_page_response.html.",
                login_page_response.status_code,
            )

        token_match = re.search(
            r'name="__cmtkn" value="(?P<token>\w+)"', login_page_response.text
        )
        if token_match is None or token_match.lastindex is None:
            _logger.error("Token not found.")
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
            _logger.error(
                f"Login request failed with status {login_response.status_code}."
            )
            self._log_to_file("login_response.txt", login_response.text)
            raise CardmarketException(
                "Unexpected login error. Check login_response.txt.",
                login_response.status_code,
            )

        login_html = BeautifulSoup(login_response.text, "html.parser")
        error_message_container = login_html.find("h4", class_="alert-heading")
        if error_message_container:
            error_message = error_message_container.get_text(separator=". ") + "."
            _logger.error(f"Login error response with message: {error_message}")
            raise CardmarketException(error_message)

        _logger.info("Login successful.")

    def logout(self):
        _logger.info("logout")
        self._close_session()

    def get_wants_lists(self) -> WantsListsPage:
        page_text = self._request_authenticated_page("Wants")
        return WantsListsPage(page_text, self.language)

    def get_wants_list(self, id: str) -> WantsListPage:
        page_text = self._request_authenticated_page(f"Wants/{id}")
        return WantsListPage(page_text, self.language)

    def get_card(self, query: CardQuery):
        params = {}
        if query.languages is not None:
            params["language"] = ",".join([str(l.value.id) for l in query.languages])
        if query.min_condition is not None:
            params["minCondition"] = str(query.min_condition.value.id)
        bool_params = {
            "isReverseHolo": query.is_reverse_holo,
            "isSigned": query.is_signed,
            "isFirstEd": query.is_first_edition,
            "isAltered": query.is_altered,
        }
        for key, value in bool_params.items():
            if value is None:
                continue
            params[key] = "Y" if value else "N"
        page_text = self._request_authenticated_page(f"Cards/{query.id}", params)
        return CardPage(page_text, self.language)

    def get_seller_wanted_offers(
        self, seller_id: str, wants_list_id: str
    ) -> SellerOffersPage:
        page_text = self._request_authenticated_page(
            f"Users/{seller_id}/Offers/Singles",
            params={"idWantslist": wants_list_id},
        )
        return SellerOffersPage(page_text, self.language)

    def _log_to_file(self, path: str, content: str):
        with open(path, "w") as out:
            out.write(content)
        _logger.info(f'Log file written "{path}".')

    @sleep_and_retry
    @limits(calls=RATE_LIMIT_CALL_COUNT, period=RATE_LIMIT_PERIOD_SECONDS)
    def _request_rate_limited(self, url: str, params: dict):
        return self.session.get(url, params=params)

    def _request_authenticated_page(
        self, endpoint: str, params: dict | None = None
    ) -> str:
        _logger.info(f"GET {endpoint}{'' if params is None else ' ' + str(params)}")

        session = self.session
        url = f"{self._cardmarket_url()}/{endpoint}"

        if self._rate_limited:
            page_response = self._request_rate_limited(url, params)
        else:
            page_response = session.get(url, params=params)

        if page_response.status_code != 200:
            _logger.error(
                f"Failed to request {endpoint} with status {page_response.status_code}."
            )

            if page_response.status_code in [401, 403]:
                raise CardmarketException(
                    "Your session may have expired. Please re-login.",
                    status_code=page_response.status_code,
                )
            if page_response.status_code == 429:
                raise CardmarketException(
                    "Too many requests. Try again later.",
                    status_code=429,
                )

            error_file_name = f"{endpoint.replace('/', '_')}_page_response.html"
            self._log_to_file(error_file_name, page_response.text)
            raise CardmarketException(
                f"Unexpected page error. Check {error_file_name}.",
                status_code=page_response.status_code,
            )

        return page_response.text

    @property
    def session(self) -> requests.Session:
        assert self._session is not None
        return self._session

    def _open_new_session(
        self,
        browser: Browser,
        user_agent: str,
        language: CardmarketLanguage,
        game: CardmarketGame,
        with_retries: bool = True,
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
        _logger.debug(f"{len(cookies)} cookies extracted from browser {browser.value}.")
        self._session.cookies.clear()
        for cookie in cookies:
            self._session.cookies.set_cookie(cookie)

        if with_retries:
            retries = LogRetry(
                status_forcelist=[429, 502, 503, 504],
                # the retry-after headers says 60 seconds, which is often longer than necessary
                respect_retry_after_header=False,
                constant_sleep=32,
            )
            self._session.mount("https://", HTTPAdapter(max_retries=retries))

        _logger.debug("New session opened.")
        return self._session

    def _close_session(self):
        if self._session:
            self._session.close()
            _logger.debug("Session closed.")
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
