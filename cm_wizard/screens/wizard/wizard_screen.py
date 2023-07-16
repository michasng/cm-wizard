import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.wizard.controls.wizard import Wizard


class WizardScreen(AbstractScreen):
    route: str = "/wizard/:id"

    def __init__(self, id: str):
        wizard_ref = ft.Ref[Wizard]()

        def on_visit():
            wizard_ref.current.on_visit()

        def back(_):
            wizard_ref.current.stop_wizard()
            self.page.route = f"/wants/{id}"
            self.page.update()

        super().__init__(
            route=self.route,
            on_visit=on_visit,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.icons.NAVIGATE_BEFORE_OUTLINED, on_click=back),
                title=ft.Text("Cardmarket Wizard 🧙‍♂️🪄"),
            ),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                Wizard(
                    ref=wizard_ref,
                    id=id,
                ),
            ],
        )
