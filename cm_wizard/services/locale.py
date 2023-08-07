import json
from typing import Any

from cm_wizard.services.cardmarket.enums.cardmarket_language import CardmarketLanguage


class Locale:
    language: CardmarketLanguage
    translations: dict[str, Any]

    def __init__(self, language: CardmarketLanguage):
        self.language = language
        path = f"cm_wizard/i18n/{language.value}.json"
        with open(path, "r") as f:
            self.translations = json.load(f)

    def get_label(self, path: str) -> str:
        segments = path.split(".")
        namespace: Any = self.translations
        for segment in segments:
            namespace = namespace[segment]
        return namespace

    def __str__(self):
        return self.language.value
