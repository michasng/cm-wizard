import time

import flet as ft

from cm_wizard.screens.wizard.controls.wizard_loading_view import WizardLoadingView


class Wizard(ft.UserControl):
    _wants_list_id: str
    _loading_ref: ft.Ref[WizardLoadingView]

    def __init__(self, ref: ft.Ref["Wizard"], id: str):
        super().__init__(ref=ref)
        self._wants_list_id = id
        self._loading_ref = ft.Ref[WizardLoadingView]()

    def on_visit(self):
        # TODO: replace this with running the actual wizard
        while True:
            time.sleep(0.1)
            self._loading_ref.current.value += 0.01
            self.update()

    def build(self) -> ft.Control:
        return WizardLoadingView(ref=self._loading_ref)
