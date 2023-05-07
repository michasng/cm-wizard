import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.wants_list.controls.wants_list_table import WantsListTable


class WantsListScreen(AbstractScreen):
    route: str = "/wants/:id"
    _wants_list_table_ref: ft.Ref[WantsListTable]
    _wants_list_id: str

    def __init__(self, id: str):
        self._wants_list_id = id
        self._wants_list_table_ref = ft.Ref[WantsListTable]()

        def on_visit():
            self._wants_list_table_ref.current.on_visit()

        def back(_):
            self.page.route = "/wants"
            self.page.update()

        super().__init__(
            route=self.route,
            on_visit=on_visit,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.icons.NAVIGATE_BEFORE_OUTLINED, on_click=back),
                title=ft.Text("Wants List"),
            ),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            scroll=True,
            controls=[
                WantsListTable(
                    ref=self._wants_list_table_ref,
                    id=self._wants_list_id,
                ),
            ],
        )
