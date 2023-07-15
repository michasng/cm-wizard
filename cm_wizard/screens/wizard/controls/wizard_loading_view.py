import flet as ft

from cm_wizard.services.wizard_orchestrator_service import WizardOrchestratorStage


class WizardLoadingView(ft.UserControl):
    _progress_ring_ref: ft.Ref[ft.ProgressRing]
    _text_ref: ft.Ref[ft.Text]

    _stage_to_label = {
        WizardOrchestratorStage.GET_WANTS_LIST: "getting wants list",
        WizardOrchestratorStage.GET_CARDS_SELLERS: "finding card sellers",
        WizardOrchestratorStage.RANK_SELLERS: "ranking sellers",
        WizardOrchestratorStage.GET_SELLERS_OFFERS: "getting seller offers",
        WizardOrchestratorStage.FIND_BEST_COMBINATION: "finding best combination",
    }

    def __init__(
        self,
        ref: ft.Ref["WizardLoadingView"],
    ):
        super().__init__(ref=ref)
        self._progress_ring_ref = ft.Ref[ft.ProgressRing]()
        self._text_ref = ft.Ref[ft.Text]()

    def progress(self, new_value: float, stage: WizardOrchestratorStage):
        self._progress_ring_ref.current.value = new_value
        self._text_ref.current.value = self._stage_to_label[stage]
        self.update()

    def build(self) -> ft.Control:
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.ProgressRing(
                    ref=self._progress_ring_ref,
                    width=200,
                    height=200,
                    value=0,
                ),
                ft.Text(
                    ref=self._text_ref,
                    value=self._stage_to_label[WizardOrchestratorStage.GET_WANTS_LIST],
                ),
            ],
        )
