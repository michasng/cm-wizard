import flet as ft

from cm_wizard.controls.cardmarket_icon import CardmarketIcon, CardmarketIcons
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service


class WantsListTable(ft.UserControl):
    _wants_list_id: str
    _search_button_ref: ft.Ref[ft.FilledButton]
    _title_ref: ft.Ref[ft.Row]
    _table_ref: ft.Ref[ft.DataTable]

    def __init__(self, ref: ft.Ref["WantsListTable"], id: str):
        super().__init__(ref=ref)
        self._wants_list_id = id
        self._search_button_ref = ft.Ref[ft.FilledButton]()
        self._title_ref = ft.Ref[ft.Row]()
        self._table_ref = ft.Ref[ft.DataTable]()

    def on_visit(self):
        self.wants_list = cardmarket_service.get_wants_list(self._wants_list_id)

        self._title_ref.current.controls = [
            ft.Text(self.wants_list.title, size=30),
            ft.FilledButton(
                ref=self._search_button_ref,
                text="Find best prices",
                icon="search",
                on_click=self.find_best_prices,
            )
            if len(self.wants_list.items) > 0
            else ft.Text("(empty)"),
        ]

        def map_bool(value: bool | None) -> ft.Control:
            if value is None:
                return ft.Container()
            return ft.Checkbox(value=value, disabled=True)

        self._table_ref.current.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(control)
                    for control in [
                        ft.Text(item.amount),
                        ft.Text(item.name),
                        ft.Text(", ".join(item.expansions)),
                        ft.Text(
                            ", ".join(
                                [
                                    language.value.labels[cardmarket_service.language]
                                    for language in item.languages
                                ]
                            )
                        ),
                        ft.Text(item.min_condition.name),
                        map_bool(item.is_reverse_holo),
                        map_bool(item.is_signed),
                        map_bool(item.is_first_edition),
                        map_bool(item.is_altered),
                    ]
                ],
            )
            for item in self.wants_list.items
        ]
        self.update()

    def find_best_prices(self, _):
        if len(self.wants_list.items) > 0:
            res = cardmarket_service.get_card(self.wants_list.items[0])
            if len(res.offers) == 0:
                print("no offers found")
                return
            print(
                f'Staring price for "{res.name}" is {res.offers[0].price_euro_cents} cents.'
            )
            seller_offers = cardmarket_service.get_seller_wanted_offers(
                seller_id=res.offers[0].seller.id,
                wants_list_id=self._wants_list_id,
            )
            print(
                f"Found {len(seller_offers.offers)} wanted offers from seller {res.offers[0].seller.id}."
            )

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Row(
                    ref=self._title_ref,
                    controls=[],
                ),
                ft.DataTable(
                    ref=self._table_ref,
                    columns=[
                        ft.DataColumn(ft.Text("Amount"), numeric=True),
                        ft.DataColumn(ft.Text("Name")),
                        ft.DataColumn(ft.Text("Expansions")),
                        ft.DataColumn(ft.Text("Languages")),
                        ft.DataColumn(ft.Text("Min Condition")),
                        ft.DataColumn(
                            tooltip="Reverse Holo?",
                            label=CardmarketIcon(
                                icon_data=CardmarketIcons.REVERSE_HOLO
                            ),
                        ),
                        ft.DataColumn(
                            tooltip="Signed?",
                            label=CardmarketIcon(icon_data=CardmarketIcons.SIGNED),
                        ),
                        ft.DataColumn(
                            tooltip="First Edition?",
                            label=CardmarketIcon(
                                icon_data=CardmarketIcons.FIRST_EDITION
                            ),
                        ),
                        ft.DataColumn(
                            label=CardmarketIcon(icon_data=CardmarketIcons.ALTERED),
                            tooltip="Altered?",
                        ),
                    ],
                    rows=[],
                ),
            ],
        )
