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
from cm_wizard.services.cardmarket.model.card_condition import CardCondition
from cm_wizard.services.cardmarket.model.card_language import CardLanguage
from cm_wizard.services.cardmarket.model.wants_list import WantsList, WantsListItem
from cm_wizard.services.cardmarket.model.wants_lists import WantsLists, WantsListsItem

CARDMARKET_COOKIE_DOMAIN = ".cardmarket.com"
CARDMARKET_BASE_URL = f"https://www{CARDMARKET_COOKIE_DOMAIN}"


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
        browser: Browser = Browser.EDGE,
        language: CardmarketLanguage = CardmarketLanguage.ENGLISH,
        game: CardmarketGame = CardmarketGame.YU_GI_OH,
    ):
        self._logger.info("login")

        session = self._open_new_session(browser, language, game)

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

    def find_wants_lists(self) -> WantsLists:
        self._logger.info("find wants lists")

        wants_lists_page_response = self._get_authenticated_page(
            page_name="wants lists",
            url=f"{self._cardmarket_url()}/Wants",
        )

        wants_list_page_html = BeautifulSoup(
            wants_lists_page_response.text, "html.parser"
        )
        cards_html: ResultSet[Tag] = wants_list_page_html.find_all(class_="card")
        self._logger.info(f"{len(cards_html)} wants lists found.")

        items: list[WantsListsItem] = []
        for card_html in cards_html:
            link_html = card_html.find(class_="card-link-img-top")
            id_match = re.search(r"(?P<id>\d+)$", link_html.attrs["href"])
            assert id_match is not None
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

    def find_wants_list(self, wants_list_id: str) -> WantsList:
        self._logger.info(f"find wants {wants_list_id}")

        wants_page_response = self._get_authenticated_page(
            page_name="wants",
            url=f"{self._cardmarket_url()}/Wants/{wants_list_id}",
        )

        wants_page_html = BeautifulSoup(wants_page_response.text, "html.parser")
        table_html = wants_page_html.find(class_="data-table")
        table_header_html = table_html.find("thead")
        table_body_html = table_html.find("tbody")
        rows_html: ResultSet[Tag] = table_body_html.find_all("tr")
        self._logger.info(f"{len(rows_html)} wanted found.")

        def find_bool_th(title: str) -> Tag | None:
            th_content = table_header_html.find("span", attrs={"title": title})
            if th_content is None:
                return None
            return th_content.parent

        table_column_indexes = {
            key: table_header_html.index(th_element) if th_element is not None else None
            for key, th_element in {
                "name": table_header_html.find(class_="name"),
                "preview": table_header_html.find(class_="preview"),
                "amount": table_header_html.find(class_="amount"),
                "expansion": table_header_html.find(class_="expansion"),
                "languages": table_header_html.find(class_="languages"),
                "min_condition": table_header_html.find(class_="condition"),
                "is_reverse_holo": find_bool_th("Reverse Holo?"),
                "is_signed": find_bool_th("Signed?"),
                "is_first_edition": find_bool_th("First Edition?"),
                "is_altered": find_bool_th("Altered?"),
                "buy_price": table_header_html.find(class_="buyPrice"),
                "has_mail_alert": table_header_html.find(class_="mailAlert"),
            }.items()
        }

        items: list[WantsListItem] = []
        for row in rows_html:

            def find_td(key: str) -> Tag:
                index = table_column_indexes[key]
                return row.contents[index]

            def find_td_tooltips(key: str) -> ResultSet[Tag]:
                return find_td(key).find_all(
                    attrs={"data-toggle": "tooltip"},
                )

            def find_td_optional_bool(key: str) -> bool | None:
                index = table_column_indexes[key]
                if index is None:
                    return None
                text = row.contents[index].text
                if text == "Y":
                    return True
                if text == "N":
                    return False
                return None

            name_link_html = find_td("name").find("a")
            id_match = re.search(r"Cards\/(?P<id>[\w-]+)", name_link_html.attrs["href"])
            assert id_match is not None

            tooltip_img_html = find_td("preview").find("span").attrs["title"]
            image_url_match = re.search(r"src=\"(?P<image_url>.*?)\"", tooltip_img_html)
            assert image_url_match is not None

            buy_price_unit_matches = re.findall(
                r"\d+", find_td("buy_price").find("span").text
            )

            items.append(
                WantsListItem(
                    id=id_match.group("id"),
                    name=name_link_html.text,
                    amount=int(find_td("amount").text),
                    image_url=f"https:{image_url_match.group('image_url')}",
                    expansions=[
                        tooltip.find("span").text
                        for tooltip in find_td_tooltips("expansion")
                    ],
                    languages=[
                        CardLanguage.find_by_label(
                            self._language, tooltip.attrs["data-original-title"]
                        )
                        for tooltip in find_td_tooltips("languages")
                    ],
                    min_condition=CardCondition.find_by_abbreviation(
                        find_td("min_condition").find(class_="badge").text
                    ),
                    is_reverse_holo=find_td_optional_bool("is_reverse_holo"),
                    is_signed=find_td_optional_bool("is_signed"),
                    is_first_edition=find_td_optional_bool("is_first_edition"),
                    is_altered=find_td_optional_bool("is_altered"),
                    buy_price_euro_cents=None
                    if len(buy_price_unit_matches) == 0
                    else int(f"{buy_price_unit_matches[0]}{buy_price_unit_matches[1]}"),
                    has_mail_alert=find_td("has_mail_alert").text == "Y",
                )
            )

        return WantsList(
            title=wants_page_html.find("h1").text,
            items=items,
        )

    def _log_to_file(self, path: str, content: str):
        self._logger.info(f'Start logging to file "{path}".')
        with open(path, "w") as out:
            out.write(content)
        self._logger.info(f'Done logging to file "{path}".')

    def _get_authenticated_page(self, page_name: str, url: str) -> requests.Response:
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
            self._log_to_file(f"{page_name}_page_response.html", page_response.text)
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
                "User-Agent": self._create_user_agent_header(browser),
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
