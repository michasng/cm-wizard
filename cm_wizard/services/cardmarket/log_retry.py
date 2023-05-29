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

    def __init__(self, *args, constant_sleep: float | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_sleep = constant_sleep

        if "history" in kwargs:
            history: tuple[RequestHistory] = kwargs["history"]
            request = history[-1]
            _logger.warn(
                f"Retrying {request.method} {request.url} for status {request.status}."
            )

    # override
    def new(self, **kw):
        kw["constant_sleep"] = self.constant_sleep
        return super().new(**kw)

    # override
    def get_backoff_time(self) -> float:
        if self.constant_sleep is None:
            return super().get_backoff_time()

        return self.constant_sleep
