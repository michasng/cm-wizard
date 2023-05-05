from typing import Optional

import flet as ft

from cm_wizard.controls.form import Form
from cm_wizard.controls.validated_text_field import ValidatedTextField
from cm_wizard.services.cardmarket.cardmarket_service import (
    cardmarket_service,
    CardmarketException,
)


class LoginForm(ft.UserControl):
    def login(self, username: str, password: str):
        try:
            cardmarket_service.login(username, password)
        except CardmarketException as err:
            self.errorText.value = err
            # TODO: fix snackbar. Why is it not showing?
            self.page.show_snack_bar(ft.SnackBar(ft.Text(err)))
            self.update()
            return
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

        self.errorText = ft.Text(None, color="#ee5555")
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
                    # TODO: answer this question for the user
                    info_child=ft.Text("Why do I need to enter my credentials?"),
                ),
                ft.Container(height=32),
                self.errorText,
            ],
        )
