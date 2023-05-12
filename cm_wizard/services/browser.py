from enum import Enum


class Browser(Enum):
    CHROME = "chrome"
    CHROMIUM = "chromium"
    EDGE = "edge"
    FIREFOX = "firefox"
    SAFARI = "safari"
    OPERA = "opera"

    @classmethod
    def find_by_value(cls, value: str) -> "Browser":
        for browser in Browser:
            if browser.value == value:
                return browser
        raise NotImplementedError(f"Browser {value} is not supported.")
