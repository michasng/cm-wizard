import threading

import flet as ft

from cm_wizard.screens.wizard.controls.wizard_loading_view import WizardLoadingView
from cm_wizard.screens.wizard.controls.wizard_result_view import WizardResultView
from cm_wizard.services.wizard_orchestrator_service import (
    WizardOrchestratorStage,
    wizard_orchestrator_service,
)


class Wizard(ft.UserControl):
    _wants_list_id: str
    _stage: WizardOrchestratorStage
    _loading_ref: ft.Ref[WizardLoadingView]

    def __init__(self, ref: ft.Ref["Wizard"], id: str):
        super().__init__(ref=ref, expand=True)
        self._wants_list_id = id
        self._stage = WizardOrchestratorStage.GET_WANTS_LIST
        self._loading_ref = ft.Ref[WizardLoadingView]()
        self.stop_event = threading.Event()

    def on_progress(self, progress: float, stage: WizardOrchestratorStage):
        if self.stop_event.is_set():
            raise InterruptedError("Wizard was stopped.")
        self._stage = stage
        self._loading_ref.current.progress(progress, stage)
        self.update()

    def on_visit(self):
        self.stop_event.clear()
        try:
            result = wizard_orchestrator_service.run(
                self._wants_list_id, self.on_progress
            )
            self.controls = [WizardResultView(self._wants_list_id, result)]
            self.update()
        except InterruptedError:
            pass
        finally:
            self.stop_event.clear()

    def stop_wizard(self):
        self.stop_event.set()

    def build(self) -> ft.Control:
        return ft.Container(
            alignment=ft.Alignment(0, 0),
            content=WizardLoadingView(ref=self._loading_ref),
        )
