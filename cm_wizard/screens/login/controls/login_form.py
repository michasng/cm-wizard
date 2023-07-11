import textwrap

import flet as ft

from cm_wizard.controls.conditional import Conditional
from cm_wizard.controls.form import Form
from cm_wizard.controls.validated_text_field import ValidatedTextField
from cm_wizard.services.browser import Browser
from cm_wizard.services.cardmarket.cardmarket_service import (
    CardmarketException,
    cardmarket_service,
)


class LoginForm(ft.UserControl):
    credentials_info = Conditional(False)

    def login(self, browser_value: str, user_agent: str, username: str, password: str):
        browser = Browser.find_by_value(browser_value)
        self.status_indicator.controls = [ft.ProgressRing()]
        self.update()
        try:
            cardmarket_service.login(username, password, browser, user_agent)
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
        def validate_user_agent(value: str) -> str | None:
            if value == "":
                return "Please enter a user agent."
            return None

        def validate_username(value: str) -> str | None:
            if value == "":
                return "Please enter a username."
            return None

        def validate_password(value: str) -> str | None:
            if value == "":
                return "Please enter a password."
            return None

        def toggle_info(_) -> None:
            self.credentials_info.set_value(not self.credentials_info.value)

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
                    fields=[
                        ft.Dropdown(
                            width=400,
                            label="Browser",
                            options=[
                                ft.dropdown.Option(browser.value) for browser in Browser
                            ],
                            value=Browser.CHROME.value,
                        ),
                        ValidatedTextField(
                            label="User Agent",
                            hint="Mozilla/5.0...",
                            validate=validate_user_agent,
                        ),
                        ft.Markdown(
                            f"Find out your browser's user agent on: [useragentstring.com](https://useragentstring.com).",
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=lambda e: self.page.launch_url(e.data),
                        ),
                        ft.Markdown(
                            f"Also enable cookies and refresh [cardmarket.com](https://www.cardmarket.com/).",
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=lambda e: self.page.launch_url(e.data),
                        ),
                        ft.Divider(),
                        ValidatedTextField(
                            label="Username",
                            validate=validate_username,
                        ),
                        ValidatedTextField(
                            label="Password",
                            password=True,
                            validate=validate_password,
                        ),
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
