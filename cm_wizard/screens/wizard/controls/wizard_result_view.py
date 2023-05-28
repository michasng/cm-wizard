import flet as ft

from cm_wizard.services.currency import format_price
from cm_wizard.services.wizard_orchestrator_service import WizardOrchestratorResult


class WizardResultView(ft.UserControl):
    def __init__(
        self,
        wants_list_id: str,
        result: WizardOrchestratorResult,
    ):
        super().__init__(expand=True)
        self._wants_list_id = wants_list_id
        self._result = result

    def build(self) -> ft.Control:
        return ft.ListView(
            controls=[
                ft.ListTile(
                    title=ft.Text(
                        f"Total: {format_price(self._result.total_price_euro_cents)} euro cents"
                    ),
                    subtitle=None
                    if len(self._result.missing_cards) == 0
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
                                    subtitle=ft.Text(
                                        format_price(
                                            sum(
                                                [
                                                    offer.price_euro_cents
                                                    for offer in seller.offers
                                                ]
                                            )
                                        )
                                    ),
                                    trailing=ft.Icon(name=ft.icons.OPEN_IN_BROWSER),
                                    url=f"https://www.cardmarket.com/en/YuGiOh/Users/{seller.id}/Offers/Singles?idWantslist={self._wants_list_id}",
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
