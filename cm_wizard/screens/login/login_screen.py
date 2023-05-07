import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.login.controls.login_form import LoginForm


class LoginScreen(AbstractScreen):
    route: str = "/login"

    def __init__(self):
        super().__init__(
            route=self.route,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[LoginForm()],
        )
