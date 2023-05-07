import textwrap
from typing import Optional

import flet as ft

from cm_wizard.controls.conditional import Conditional
from cm_wizard.controls.form import Form
from cm_wizard.controls.validated_text_field import ValidatedTextField
from cm_wizard.services.cardmarket.cardmarket_service import (
    CardmarketException,
    cardmarket_service,
)


class LoginForm(ft.UserControl):
    credentials_info = Conditional(False)

    def login(self, username: str, password: str):
        self.status_indicator.controls = [ft.ProgressRing()]
        self.update()
        try:
            cardmarket_service.login(username, password)
        except CardmarketException as err:
            self.status_indicator.controls = [ft.Text(err, color="#ee5555")]
            self.update()
            return
        self.page.show_snack_bar(
            ft.SnackBar(ft.Text("Logged in successfully."), open=True)
        )
        self.page.route = "/wants"
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

        def toggle_info(_) -> None:
            self.credentials_info.set_value(not self.credentials_info.value)

        username = ValidatedTextField(
            label="Username",
            validate=validate_username,
        )
        password = ValidatedTextField(
            label="Password",
            password=True,
            validate=validate_password,
        )

        # has to be a Column, because a Container cuts off parts of the ProgressRing for some reason
        self.status_indicator = ft.Column()
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=False,
            tight=True,
            controls=[
                Form(
                    title_label="Login to cardmarket",
                    submit_label="Login",
                    on_valid_submit=self.login,
                    form_fields=[
                        username,
                        password,
                    ],
                    info_child=ft.TextButton(
                        "Why do I need to enter my credentials?", on_click=toggle_info
                    ),
                ),
                ft.Container(height=16),
                self.credentials_info.with_content(
                    ft.Text(
                        textwrap.dedent(
                            """\
                            Your credentials are used to login to your account and access your wishlist. That's it. They are not stored.
                            Feel free to look at the code and double-check. 🦉
                            """
                        ),
                        width=400,
                        text_align=ft.TextAlign.LEFT,
                    ),
                ),
                ft.Container(height=16),
                self.status_indicator,
            ],
        )
