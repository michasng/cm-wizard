import flet as ft

from cm_wizard.controls.cardmarket_icon import CardmarketIcon, CardmarketIcons
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service


class WantsListTable(ft.UserControl):
    _wants_list_id: str
    _title_ref: ft.Ref[ft.Text]
    _table_ref: ft.Ref[ft.DataTable]

    def __init__(self, ref: ft.Ref["WantsListTable"], id: str):
        super().__init__(ref=ref)
        self._wants_list_id = id
        self._title_ref = ft.Ref[ft.Text]()
        self._table_ref = ft.Ref[ft.DataTable]()

    def on_visit(self):
        wants_list = cardmarket_service.get_wants_list(self._wants_list_id)

        self._title_ref.current.value = wants_list.title

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
                                    language.value.labels[
                                        cardmarket_service.get_language()
                                    ]
                                    for language in item.languages
                                ]
                            )
                        ),
                        ft.Text(item.min_condition.value.name),
                        map_bool(item.is_reverse_holo),
                        map_bool(item.is_signed),
                        map_bool(item.is_first_edition),
                        map_bool(item.is_altered),
                    ]
                ],
            )
            for item in wants_list.items
        ]
        self.update()

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text(ref=self._title_ref, size=30),
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
