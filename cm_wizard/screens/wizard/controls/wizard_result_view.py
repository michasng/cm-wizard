import flet as ft

from cm_wizard.services.wizard_orchestrator_service import WizardOrchestratorResult


class WizardResultView(ft.UserControl):
    def __init__(
        self, result: WizardOrchestratorResult, ref: ft.Ref["WizardResultView"] = None
    ):
        super().__init__(ref=ref)
        self._result = result

    def build(self) -> ft.Control:
        return ft.ListView(
            controls=[
                ft.ListTile(
                    title=ft.Text(
                        f"Total: {self._result.total_price_euro_cents} euro cents"
                    ),
                ),
                *[
                    ft.Card(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    title=ft.Text(seller.id),
                                ),
                                ft.Divider(),
                                *[
                                    ft.ListTile(
                                        title=ft.Text(offer.card_name),
                                        subtitle=ft.Text(offer.price_euro_cents),
                                    )
                                    for offer in seller.offers
                                ],
                            ]
                        )
                    )
                    for seller in self._result.sellers
                ],
            ]
        )
