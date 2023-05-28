import flet as ft

from cm_wizard.services.currency import format_price
from cm_wizard.services.wizard_orchestrator_service import WizardOrchestratorResult


class WizardResultView(ft.UserControl):
    def __init__(self, result: WizardOrchestratorResult):
        super().__init__(expand=True)
        self._result = result

    def build(self) -> ft.Control:
        return ft.ListView(
            controls=[
                ft.ListTile(
                    title=ft.Text(
                        f"Total: {format_price(self._result.total_price_euro_cents)} euro cents"
                    ),
                    subtitle=None
                    if self._result.missing_cards is None
                    else ft.Text(
                        f"Failed to find {', '.join(self._result.missing_cards)}"
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
                                        subtitle=ft.Text(
                                            format_price(offer.price_euro_cents)
                                        ),
                                    )
                                    for offer in seller.offers
                                ],
                            ]
                        )
                    )
                    for seller in self._result.sellers
                ],
            ],
        )
