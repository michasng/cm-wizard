import flet as ft

from cm_wizard.screens.login.controls.login_form import LoginForm


class LoginScreen(ft.View):
    def __init__(self):
        super().__init__(
            route="/login",
            controls=[LoginForm()],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
        )
