from typing import Optional

import flet as ft

from cm_wizard.controls.form import Form
from cm_wizard.controls.validated_text_field import ValidatedTextField


class LoginScreen(ft.UserControl):
    def build(self) -> ft.Control:
        def validate_username(value: str) -> Optional[str]:
            if value == "":
                return "Please enter a username."
            return None

        def validate_password(value: str) -> Optional[str]:
            if value == "":
                return "Please enter a password."
            return None

        username = ValidatedTextField(
            label="Username",
            validate=validate_username,
        )
        password = ValidatedTextField(
            label="Password",
            password=True,
            validate=validate_password,
        )

        return Form(
            title="Login to cardmarket",
            on_valid_submit=lambda values: print(f"submit {list(values)}"),
            form_fields=[
                username,
                password,
            ],
            info_children=[
                ft.Text("Why do I need to enter my credentials?"),
                # TODO: answer this question for the user
            ],
        )
