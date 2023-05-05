from typing import Callable, Optional

import flet as ft

ValidateCallable = Callable[[str], Optional[str]]
SubmitCallable = Callable[[str], None]


class ValidatedTextField(ft.UserControl):
    _ref: ft.Ref[ft.TextField]
    label: str
    value: str
    password: bool
    on_submit: SubmitCallable
    _validate: ValidateCallable
    _validate_on_changed: bool

    def __init__(
        self,
        label: str,
        validate: ValidateCallable,
        value: str = None,
        password: bool = False,
        on_submit: SubmitCallable = None,
    ):
        super().__init__()
        self._ref = ft.Ref[ft.TextField]()
        self.label = label
        self.value = value
        self.password = password
        self._validate = validate
        self._validate_on_changed = False
        self.on_submit = on_submit

    def get_value(self) -> str:
        return self._ref.current.value

    def focus(self) -> None:
        self._ref.current.focus()

    def validate(self) -> bool:
        self._validate_on_changed = True
        error_text = self._validate(self.get_value())
        self._ref.current.error_text = error_text
        self.update()
        return error_text is None

    def build(self) -> ft.Control:
        def on_change(_):
            if self._validate_on_changed:
                self.validate()

        return ft.TextField(
            value=self.value,
            ref=self._ref,
            label=self.label,
            password=self.password,
            on_change=on_change,
            on_submit=None if self.on_submit is None else self.on_submit,
        )
