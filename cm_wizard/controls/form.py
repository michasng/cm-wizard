from typing import Callable, Optional

import flet as ft

from cm_wizard.controls.validated_text_field import ValidatedTextField

ValidSubmitCallable = Callable[[list[str]], None]


class Form(ft.UserControl):
    title: str
    form_fields: list[ValidatedTextField]
    info_children: list[ft.Control]
    on_valid_submit: ValidSubmitCallable

    def __init__(
        self,
        on_valid_submit: ValidSubmitCallable,
        title: str,
        form_fields: list[ValidatedTextField],
        info_children: list[ft.Control],
    ):
        super().__init__()
        self.on_valid_submit = on_valid_submit
        self.title = title
        self.form_fields = form_fields
        self.info_children = info_children

    def build(self) -> ft.Control:
        def on_submit(_):
            all_valid = all(form_field.validate() for form_field in self.form_fields)
            if all_valid:
                self.on_valid_submit(
                    form_field.get_value() for form_field in self.form_fields
                )

        return ft.Column(
            width=400,
            height=400,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(self.title, size=30),
                *self.form_fields,
                ft.ElevatedButton(text="Submit", on_click=on_submit),
                *self.info_children,
            ],
        )
