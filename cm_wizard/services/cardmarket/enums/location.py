from enum import Enum

from cm_wizard.services.locale import Locale


class Location(Enum):
    AUSTRIA = "AT"
    BELGIUM = "BE"
    BULGARIA = "BG"
    CROATIA = "HR"
    CYPRUS = "CY"
    CZECH_REPUBLIC = "CZ"
    DENMARK = "DK"
    ESTONIA = "EE"
    FINLAND = "FI"
    FRANCE = "FR"
    GERMANY = "D"
    GREECE = "GR"
    HUNGARY = "HU"
    ICELAND = "IS"
    IRELAND = "IE"
    ITALIY = "IT"
    LATVIA = "LV"
    LIECHTENSTEIN = "LI"
    LITHUANIA = "LT"
    LUXEMBOURG = "LU"
    MALTA = "MT"
    NETHERLANDS = "NL"
    NORWAY = "NO"
    POLAND = "PL"
    PORTUGAL = "PT"
    ROMANIA = "RO"
    SLOVAKIA = "SK"
    SLOVENIA = "SI"
    SPAIN = "ES"
    SWEDEN = "SE"
    SWITZERLAND = "CH"
    UNITED_KINGDOM = "GB"

    def get_label(self, locale: Locale) -> str:
        return locale.get_label(f"locations.{self.value}")

    @classmethod
    def find_by_label(cls, locale: Locale, label: str) -> "Location":
        for location in Location:
            if location.get_label(locale) == label:
                return location
        raise NotImplementedError(
            f'Location "{label}" was not found in locale {locale}.'
        )
