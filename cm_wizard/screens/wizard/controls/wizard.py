import time

import flet as ft

from cm_wizard.screens.wizard.controls.wizard_loading_view import WizardLoadingView
from cm_wizard.screens.wizard.controls.wizard_result_view import WizardResultView
from cm_wizard.services.wizard_orchestrator_service import wizard_orchestrator_service


class Wizard(ft.UserControl):
    _wants_list_id: str
    _loading_ref: ft.Ref[WizardLoadingView]

    def __init__(self, ref: ft.Ref["Wizard"], id: str):
        super().__init__(ref=ref, expand=True)
        self._wants_list_id = id
        self._loading_ref = ft.Ref[WizardLoadingView]()

    def on_progress(self, progress: float):
        self._loading_ref.current.value = progress
        self.update()

    def on_visit(self):
        result = wizard_orchestrator_service.run(self._wants_list_id, self.on_progress)
        self.controls = [WizardResultView(result)]
        self.update()

    def build(self) -> ft.Control:
        return ft.Container(
            alignment=ft.Alignment(0, 0),
            content=WizardLoadingView(ref=self._loading_ref),
        )
