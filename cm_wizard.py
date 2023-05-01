import logging

import flet as ft

from cm_wizard.screens.login.login_screen import LoginScreen


def main(page: ft.Page):
    logger = logging.getLogger("cm_wizard_main")
    logger.setLevel(logging.DEBUG)

    page.title = "Cardmarket Wizard 🧙‍♂️"

    views: list[ft.View] = [
        LoginScreen(),
        ft.View(
            route="/wishlists",
            appbar=ft.AppBar(title=ft.Text("Wishlists")),
            controls=[ft.Text("TODO: Select your wishlist...")],
        ),
    ]
    page.route = views[0].route

    def route_change(route: str):
        logger.debug(f"route change: {route}")
        page.views.clear()
        troute = ft.TemplateRoute(page.route)

        for view in views:
            if troute.match(view.route):
                page.views.append(view)
                break
        page.update()

    def view_pop(_):
        logger.debug(f"view pop")
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


# This logging level is passed to the flet server.
# Overriding it via environment variables did not work.
logging.basicConfig(level=logging.WARNING)
ft.app(target=main)
