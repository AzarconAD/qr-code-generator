import flet as ft
from app.views.home_view import HomeView

def main(page: ft.Page):
    page.title = "QR Code Generator"
    page.theme_mode = ft.ThemeMode.LIGHT

    page.window.width = 650
    page.window.height = 550

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    home = HomeView(page)
    page.add(home.get_view())

    page.update()