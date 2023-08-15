import base64
from enum import Enum
from io import BytesIO

import flet as ft
from PIL import Image

_icon_sprite_sheet = Image.open("assets/icons.webp")

_ICON_SIZE = 16


class CardmarketIcons(Enum):
    FLAG_UNKNOWN = [0, 0]
    FLAG_ENGLAND = [1, 0]
    FLAG_FRANCE = [3, 0]
    FLAG_GERMANY = [5, 0]
    FLAG_SPAIN = [7, 0]
    FLAG_ITALY = [9, 0]
    FLAG_CHINA = [11, 0]
    FLAG_JAPAN = [13, 0]
    FLAG_PORTUGAL = [15, 0]
    FLAG_RUSSIA = [17, 0]
    FLAG_KOREA = [19, 0]
    FLAG_TAIWAN = [21, 0]
    FLAG_NETHERLANDS = [23, 0]
    FLAG_POLAND = [25, 0]
    FLAG_CZECH = [27, 0]
    FLAG_HUNGARY = [29, 0]
    FLAG_EUROPE = [31, 0]
    SHOPPING_CARD = [0, 1]
    SHOPPING_CARD_ADD = [1, 1]
    SHOPPING_CARD_REMOVE = [2, 1]
    FIRST_EDITION = [7, 1]
    SIGNED = [11, 1]
    ALTERED = [15, 1]
    CAMERA = [17, 1]
    REVERSE_HOLO = [26, 1]
    ACCOUNT_TYPE_PRIVATE = [28, 1]
    ACCOUNT_TYPE_PROFESSIONAL = [29, 1]
    ACCOUNT_TYPE_POWERSELLER = [30, 1]
    CALENDAR = [33, 1]
    ACCOUNT_EVALUATION_UNKNOWN = [23, 2]
    ACCOUNT_EVALUATION_VERY_GOOD = [24, 2]
    ACCOUNT_EVALUATION_GOOD = [25, 2]
    ACCOUNT_EVALUATION_NEUTRAL = [26, 2]
    ACCOUNT_EVALUATION_BAD = [27, 2]
    STATISTICS = [0, 3]
    SETTINGS = [1, 3]
    PAGINATION_FIRST = [6, 3]
    PAGINATION_PREVIOUS = [7, 3]
    PAGINATION_NEXT = [8, 3]
    PAGINATION_LAST = [9, 3]
    YES = [11, 3]
    NO = [12, 3]
    ADD = [13, 3]
    REMOVE = [14, 3]
    EDIT = [15, 3]
    CARD_CONDITION_MINT = [24, 3]
    CARD_CONDITION_NEAR_MINT = [25, 3]
    CARD_CONDITION_EXCELLENT = [26, 3]
    CARD_CONDITION_GOOD = [27, 3]
    CARD_CONDITION_LIGHT_PLAYED = [28, 3]
    CARD_CONDITION_PLAYED = [29, 3]
    CARD_CONDITION_POOR = [30, 3]


class CardmarketIcon(ft.UserControl):
    def __init__(self, icon_data: CardmarketIcons):
        super().__init__()
        x = icon_data.value[0] * _ICON_SIZE
        y = icon_data.value[1] * _ICON_SIZE
        self.image = _icon_sprite_sheet.crop((x, y, x + _ICON_SIZE, y + _ICON_SIZE))

    def build(self) -> ft.Control:
        image_buffer = BytesIO()
        self.image.save(image_buffer, format="PNG")
        base64_image = base64.b64encode(image_buffer.getvalue())
        return ft.Image(src_base64=base64_image.decode("utf-8"))


class CardmarketIconShowcase(ft.UserControl):
    def build(self) -> ft.Control:
        return ft.Row(
            controls=[CardmarketIcon(value) for value in CardmarketIcons],
            wrap=True,
            width=400,
        )
