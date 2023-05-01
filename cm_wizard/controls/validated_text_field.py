from typing import Callable, Optional

import flet as ft

ValidateCallable = Callable[[str], Optional[str]]


class ValidatedTextField(ft.UserControl):
    _ref: ft.Ref[ft.TextField]
    label: str
    password: bool
    _validate: ValidateCallable
    _validate_on_changed: bool

    def __init__(
        self,
        label: str,
        validate: ValidateCallable,
        password: bool = False,
    ):
        super().__init__()
        self._ref = ft.Ref[ft.TextField]()
        self.label = label
        self.password = password
        self._validate = validate
        self._validate_on_changed = False

    def get_value(self) -> str:
        return self._ref.current.value

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
            ref=self._ref,
            label=self.label,
            password=self.password,
            on_change=on_change,
        )
