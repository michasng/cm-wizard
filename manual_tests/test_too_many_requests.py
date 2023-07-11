import logging
import time
from datetime import datetime

from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service
from cm_wizard.services.cardmarket.enums.cardmarket_game import CardmarketGame
from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def test_too_many_requests():
    """
    Manually ran these tests (many of them multiple times to confirm):

    Can we avoid 429 by sleeping between requests?
    - root endpoint without sleep: 10 x 200, then 429
    - with 0.1 sec sleep: same results
    - with 1 sec sleep: same results
    Short sleeping between requests seems to make no difference.
    It also makes no difference when the hour changes.
    The request limit probably depends on the minute.

    - endpoints under /en/YuGiOh 30 x 200, then 429
    The limit differs by endpoint. (10 x 200 for root, 30 x 200 for game specific endpoints)
    At least "/en/YuGiOh/AboutUs" and single card endpoints behave identical.

    - root 10 x 200, then 429, then other endpoints 420 immediately
    Endpoint limits depend on each other.

    - root 1 x 200, then single card endpoint 27 x 200, then 249
    - root 5 x 200, then single card endpoint 15 x 200, then 249
    - root 10 x 200, then single card endpoint 249
    The limit is applied proportional for all endpoints.
    If I use 50% of the limit for one endpoint, then I have also used 50% of another endpoint,
    even if their individual limits are different.

    - single card endpoint with 1 sec sleep 150 x 200
    For endpoints with a large enough limit, short sleeping actually helps.
    It probably delays the first requests far enough so they don't count towards the limit for later requests.
    - single card endpoint with 0.1 sec sleep 30 x 200, then 429
    However very short sleeping makes no difference.
    There might be no benefit to arbitrary sleeping between requests over sleeping on 429.

    single card endpoint:
    - 30 x 200, then 429, sleep <30 seconds, then 429
    - 30 x 200, then 429, sleep <=30 seconds, then 30 x 200, then 429
    However exactly 30 seconds was sometimes unreliable. It's probably best to wait a bit longer.

    Does it depends on the internal clock of the cardmarket server?
    - 30 x 200, then 429, parse server time from "date" header, wait until next minute starts, then 429
    Waiting for the next minute to start (60 - server_time.second) does not help.
    How long one has to wait seems to be independent of the server time.

    10 x 200, sleep 10 seconds, 20 x 200, then 429, sleep 22 seconds, 9 x 200, then 429
    The server seems to keep track of exactly how many requests were sent in the last ~30 seconds.
    Sleeping in-between does not reset the counter.

    However, 429 will block completely and the best time to send requests again is unknown,
    unless some form of client-side rate limiting is implemented.
    It might also be best to avoid 429 so cardmarket does not hinder this project.

    Conclusion:
    Implement client-side rate limiting to avoid 429, but still keep up the "maximum allowed rate".
    If a status 429 is still received (e.g. due to some race conditions between the client & server clocks),
    then wait for constant 32 seconds (extra 2 seconds to be safe).
    """

    browser = Browser.EDGE
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"

    session = cardmarket_service._open_new_session(
        browser,
        user_agent,
        CardmarketLanguage.ENGLISH,
        CardmarketGame.YU_GI_OH,
        with_retries=False,
    )

    def parse_date_header(header: str) -> datetime:
        return datetime.strptime(header, "%a, %d %b %Y %H:%M:%S %Z")

    def spam(
        endpoint: str,
        sleep_sec: float = 0.0,
        max_successful_requests: int = 150,
    ) -> datetime:
        for i in range(max_successful_requests):
            response = session.get(f"https://www.cardmarket.com/{endpoint}")
            assert (
                response.status_code != 403
            ), f"Session authentication failed, please open cardmarket.com in {browser.value}."
            _logger.info(f"{i + 1}: {response.status_code}")
            if response.status_code == 429:
                return parse_date_header(response.headers["date"])
            if sleep_sec != 0.0:
                time.sleep(sleep_sec)
        return parse_date_header(response.headers["date"])

    server_time = spam("en/YuGiOh/Cards/Horn-of-Heaven")
    _logger.info(f"server_time {server_time}")
    sleep_time = 32
    _logger.info(f"sleeping {sleep_time} seconds")
    time.sleep(sleep_time)
    spam("en/YuGiOh/Cards/Horn-of-Heaven")

    assert False  # show console logs
