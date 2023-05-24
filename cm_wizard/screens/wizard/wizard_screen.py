import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.wizard.controls.wizard import Wizard


class WizardScreen(AbstractScreen):
    route: str = "/wizard/:id"
    _wizard_ref: ft.Ref[Wizard]
    _wants_list_id: str

    def __init__(self, id: str):
        self._wants_list_id = id
        self._wizard_ref = ft.Ref[Wizard]()

        def on_visit():
            self._wizard_ref.current.on_visit()

        super().__init__(
            route=self.route,
            on_visit=on_visit,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                Wizard(
                    ref=self._wizard_ref,
                    id=self._wants_list_id,
                ),
            ],
        )
