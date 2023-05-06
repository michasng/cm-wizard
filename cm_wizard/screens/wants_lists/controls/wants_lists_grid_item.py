import flet as ft

from cm_wizard.services.cardmarket.model.wants_lists import WantsListsItem


class WantsListsGridItem(ft.UserControl):
    _image_ref: ft.Ref[ft.Image]

    def __init__(self, item: WantsListsItem):
        super().__init__()
        self.item = item
        self._image_ref = ft.Ref[ft.Image]()

    def build(self) -> ft.Control:
        def on_hover(e: ft.ControlEvent):
            if e.data == "true":
                self._image_ref.current.color = ft.colors.BLACK26
            else:
                self._image_ref.current.color = ft.colors.BLACK54
            self.update()

        def on_click(e: ft.ContainerTapEvent):
            print(e)  # TODO: show wants list

        return ft.Container(
            on_hover=on_hover,
            on_click=on_click,
            content=ft.Stack(
                [
                    ft.Image(
                        ref=self._image_ref,
                        src=self.item.image_url,
                        fit=ft.ImageFit.FILL,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(10),
                        color=ft.colors.BLACK45,
                        color_blend_mode=ft.BlendMode.DARKEN,
                    ),
                    ft.Column(
                        width=200,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                self.item.title,
                                size=20,
                                color=ft.colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"{self.item.distinct_cards_count} Wants ({self.item.cards_count} Cards)",
                                color=ft.colors.WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )
