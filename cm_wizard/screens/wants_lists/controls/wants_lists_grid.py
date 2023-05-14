import flet as ft

from cm_wizard.screens.wants_lists.controls.wants_lists_grid_item import (
    WantsListsGridItem,
)
from cm_wizard.services.cardmarket.cardmarket_service import cardmarket_service


class WantsListsGrid(ft.UserControl):
    _grid_view_ref: ft.Ref[ft.GridView]

    def __init__(self, ref: ft.Ref["WantsListsGrid"]):
        self._grid_view_ref = ft.Ref[ft.GridView]()
        super().__init__(ref=ref)

    def on_visit(self):
        wants_lists = cardmarket_service.get_wants_lists()
        for item in wants_lists.items:
            self._grid_view_ref.current.controls.append(WantsListsGridItem(item))
        self.update()

    def build(self) -> ft.Control:
        return ft.GridView(
            ref=self._grid_view_ref,
            width=800,
            max_extent=200,
            child_aspect_ratio=59 / 86,
            spacing=5,
            run_spacing=5,
        )
