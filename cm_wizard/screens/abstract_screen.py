from typing import Callable

import flet as ft

OnVisitCallable = Callable[[], None]


class AbstractScreen(ft.View):
    def __init__(
        self,
        route: str,
        on_visit: OnVisitCallable | None = None,
        appbar: ft.AppBar | None = None,
        vertical_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.NONE,
        horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.NONE,
        scroll: bool = False,
        controls: list[ft.Control] | None = None,
    ):
        super().__init__(
            route=route,
            appbar=appbar,
            vertical_alignment=vertical_alignment,
            horizontal_alignment=horizontal_alignment,
            scroll=scroll,
            controls=controls,
        )
        self.on_visit = on_visit
