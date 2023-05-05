from typing import Callable

import flet as ft

from cm_wizard.controls.validated_text_field import ValidatedTextField

ValidSubmitCallable = Callable[..., None]


class Form(ft.UserControl):
    title_label: str
    submit_label: str
    form_fields: list[ValidatedTextField]
    info_child: ft.Control
    on_valid_submit: ValidSubmitCallable

    def __init__(
        self,
        on_valid_submit: ValidSubmitCallable,
        title_label: str,
        submit_label: str,
        form_fields: list[ValidatedTextField],
        info_child: ft.Control,
    ):
        super().__init__()
        self.on_valid_submit = on_valid_submit
        self.title_label = title_label
        self.submit_label = submit_label
        self.form_fields = form_fields
        self.info_child = info_child

    def build(self) -> ft.Control:
        def on_submit(_):
            all_valid = all([form_field.validate() for form_field in self.form_fields])
            if all_valid:
                self.on_valid_submit(
                    *[form_field.get_value() for form_field in self.form_fields]
                )

        if len(self.form_fields) != 0:
            # focus traversal on enter
            for i in range(len(self.form_fields) - 1):
                self.form_fields[i].on_submit = lambda _: self.form_fields[
                    i + 1
                ].focus()
            # submit the last field on enter
            self.form_fields[-1].on_submit = on_submit

        return ft.Column(
            width=400,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(self.title_label, size=30),
                *self.form_fields,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.info_child,
                        ft.ElevatedButton(text=self.submit_label, on_click=on_submit),
                    ],
                ),
            ],
        )
