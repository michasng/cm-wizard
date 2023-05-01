from typing import Optional

import flet as ft

from cm_wizard.controls.form import Form
from cm_wizard.controls.validated_text_field import ValidatedTextField


class LoginForm(ft.UserControl):
    def login(self, username: str, password: str):
        print(f"submit {username}, {password}")
        self.page.route = "/wishlists"
        self.page.update()

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
            title_label="Login to cardmarket",
            submit_label="Login",
            on_valid_submit=self.login,
            form_fields=[
                username,
                password,
            ],
            # TODO: answer this question for the user
            info_child=ft.Text("Why do I need to enter my credentials?"),
        )
