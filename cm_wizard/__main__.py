import logging

import flet as ft

from cm_wizard.screens.abstract_screen import AbstractScreen
from cm_wizard.screens.login.login_screen import LoginScreen
from cm_wizard.screens.wants_list.wants_list_screen import WantsListScreen
from cm_wizard.screens.wants_lists.wants_lists_screen import WantsListsScreen
from cm_wizard.screens.wizard.wizard_screen import WizardScreen


def main(page: ft.Page):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    page.title = "Cardmarket Wizard 🧙‍♂️"

    page.route = LoginScreen.route

    def route_change(route: str):
        logger.debug(f"route change: {route}")
        troute = ft.TemplateRoute(page.route)

        page.views.clear()
        if troute.match(LoginScreen.route):
            page.views.append(LoginScreen())
        elif troute.match(WantsListsScreen.route):
            page.views.append(WantsListsScreen())
        elif troute.match(WantsListScreen.route):
            page.views.append(WantsListScreen(troute.id))
        elif troute.match(WizardScreen.route):
            page.views.append(WizardScreen(troute.id))
        else:
            raise NotImplementedError(f'Unknown route "{page.route}".')

        page.update()

        top_view: AbstractScreen = page.views[-1]
        if top_view.on_visit:
            top_view.on_visit()

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
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)-8s %(message)s",
)
ft.app(target=main)
