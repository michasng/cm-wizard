import logging

from requests.adapters import Retry
from urllib3.util.retry import RequestHistory

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class LogRetry(Retry):
    """
    Log whenever a retry occurs: https://stackoverflow.com/a/69739940/5120356
    This class is re-instantiated for every retry.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "history" in kwargs:
            history: tuple[RequestHistory] = kwargs["history"]
            request = history[-1]
            _logger.warn(
                f"Retrying {request.method} {request.url} for status {request.status}."
            )
