import flet as ft
from app.data.database import get_all_labels


class HistoryView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.list_view = ft.ListView(expand=True, spacing=10, padding=20)
        self.empty_state = ft.Column(
            [
                ft.Icon(ft.Icons.QR_CODE_2, size=60, color=ft.Colors.GREY_400),
                ft.Text("No labels generated yet.", color=ft.Colors.GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        self.container = ft.Container(content=self.empty_state, expand=True)

    def refresh(self):
        """Reload records from the database and rebuild the list. Call before showing."""
        records = get_all_labels()
        self.list_view.controls.clear()

        if not records:
            self.container.content = self.empty_state
            return

        for r in records:
            self.list_view.controls.append(self._build_row(r))
        self.container.content = self.list_view

    def _build_row(self, r: dict) -> ft.Control:
        asset_id = f"{r['asset_code']}-{r['asset_number']}"
        created = r["created_at"].replace("T", "  ") if r["created_at"] else ""

        return ft.Container(
            content=ft.Row(
                [
                    ft.Image(
                        src=r["qr_image_path"],
                        width=56,
                        height=56,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    ft.Column(
                        [
                            ft.Text(asset_id, weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(r["department"], size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                r["description"] or "No description",
                                size=12,
                                color=ft.Colors.GREY_600,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(created, size=11, color=ft.Colors.GREY_500),
                ],
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
        )

    def get_view(self) -> ft.Control:
        self.refresh()
        return self.container