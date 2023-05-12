from typing import Callable

import flet as ft

from cm_wizard.controls.validated_text_field import ValidatedTextField

ValidSubmitCallable = Callable[..., None]


class Form(ft.UserControl):
    title_label: str
    submit_label: str
    fields: list[ft.Control]  # must use a different name than super().controls
    info_child: ft.Control
    on_valid_submit: ValidSubmitCallable

    def __init__(
        self,
        on_valid_submit: ValidSubmitCallable,
        title_label: str,
        submit_label: str,
        fields: list[ft.Control],
        info_child: ft.Control,
    ):
        super().__init__()
        self.on_valid_submit = on_valid_submit
        self.title_label = title_label
        self.submit_label = submit_label
        self.fields = fields
        self.info_child = info_child

    def get_values(self) -> list[str]:
        values = []
        for control in self.fields:
            if type(control) is ValidatedTextField:
                values.append(control.get_value())
            elif type(control) is ft.Dropdown:
                values.append(control.value)
        return values

    def get_form_fields(self) -> list[ft.Control]:
        return [
            control
            for control in self.fields
            if type(control) is ValidatedTextField or ft.Dropdown
        ]

    def validate_all(self) -> list[ValidatedTextField]:
        return [
            control.validate()
            for control in self.fields
            if type(control) is ValidatedTextField
        ]

    def build(self) -> ft.Control:
        def on_submit(_):
            all_valid = all(self.validate_all())
            if all_valid:
                self.on_valid_submit(*self.get_values())

        form_fields = self.get_form_fields()

        if len(form_fields) != 0:
            # focus traversal on enter
            for i in range(len(form_fields) - 1):
                form_fields[i].on_submit = lambda _: form_fields[i + 1].focus()
            # submit the last field on enter
            form_fields[-1].on_submit = on_submit

        return ft.Column(
            width=400,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(self.title_label, size=30),
                *self.fields,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.info_child,
                        ft.FilledButton(text=self.submit_label, on_click=on_submit),
                    ],
                ),
            ],
        )
