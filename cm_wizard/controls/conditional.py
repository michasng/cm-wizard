import flet as ft


class Conditional(ft.UserControl):
    value: bool
    content: ft.Control
    else_content: ft.Control

    def __init__(
        self,
        value: bool,
        content: ft.Control = None,
        else_content: ft.Control = None,
    ):
        super().__init__()
        self.value = value
        self.content = content
        self.else_content = else_content

    def with_content(self, content: ft.Control) -> ft.Control:
        self.content = content
        return self

    def _conditional_content(self) -> ft.Control:
        return self.content if self.value else self.else_content

    def set_value(self, value: bool) -> None:
        self.value = value
        self.container.content = self._conditional_content()
        self.update()

    def build(self) -> ft.Control:
        self.container = ft.Container(self._conditional_content())
        return self.container
