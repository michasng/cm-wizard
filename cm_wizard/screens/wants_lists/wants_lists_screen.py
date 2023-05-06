import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.wants_lists.controls.wants_lists_grid import WantsListsGrid
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service


class WantsListsScreen(AbstractScreen):
    _wants_list_grid_ref: ft.Ref[WantsListsGrid]

    def __init__(self):
        self._wants_list_grid_ref = ft.Ref[WantsListsGrid]()

        def on_visit():
            self._wants_list_grid_ref.current.on_visit()

        def logout(_):
            cardmarket_service.logout()
            self.page.route = "/login"
            self.page.update()

        super().__init__(
            route="/wants",
            on_visit=on_visit,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.icons.LOGOUT_OUTLINED, on_click=logout),
                title=ft.Text("Wants Lists"),
            ),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            scroll=True,
            controls=[
                ft.Text("Select a list", size=30),
                WantsListsGrid(ref=self._wants_list_grid_ref),
            ],
        )
