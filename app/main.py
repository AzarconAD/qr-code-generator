import flet as ft
from app.views.home import HomeView
from app.views.history import HistoryView
from app.data.database import init_db


def main(page: ft.Page):
    page.title = "Asset QR Code Generator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 960
    page.window.height = 640

    init_db()

    home_view = HomeView(page)
    history_view = HistoryView(page)

    def route_change(e):
        page.views.clear()

        page.views.append(
            ft.View(
                route="/",
                appbar=ft.AppBar(
                    title=ft.Text("Asset QR Code Generator"),
                    actions=[
                        ft.TextButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.HISTORY), ft.Text("Library")],
                                spacing=6,
                                tight=True,
                            ),
                            on_click = lambda e: page.go("/history"),
                        ),
                    ],
                ),
                controls=[home_view.get_view()],
            )
        )

        if page.route == "/history":
            history_view.refresh()
            page.views.append(
                ft.View(
                    route="/history",
                    appbar=ft.AppBar(
                        title=ft.Text("All Generated Labels"),
                        leading=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: page.go("/"),
                        ),
                    ),
                    controls=[history_view.get_view()],
                )
            )

        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(None)
    page.update()