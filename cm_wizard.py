import flet as ft

from cm_wizard.screens.login.login_screen import LoginScreen


def main(page: ft.Page):
    page.title = "Cardmarket Wizard 🧙‍♂️"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(LoginScreen())


ft.app(target=main)
