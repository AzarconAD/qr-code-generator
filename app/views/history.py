import os
import flet as ft
from app.data.database import get_all_labels
from app.utils.batch_pdf_compiler import compile_labels_to_pdf


class HistoryView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.records: list[dict] = []
        self.selected_ids: set[int] = set()
        self.checkboxes: dict[int, ft.Checkbox] = {}
        self.compiled_bytes: bytes | None = None

        self.select_all_checkbox = ft.Checkbox(
            label="Select All", value=False, on_change=self.on_select_all_change,
        )
        self.compile_btn = ft.ElevatedButton(
            "Compile Selected to PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self.on_compile_click,
            disabled=True,
        )
        self.selection_status = ft.Text("0 selected", size=12, color=ft.Colors.GREY_600)

        toolbar = ft.Row(
            [self.select_all_checkbox, self.selection_status, ft.Container(expand=True), self.compile_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.list_view = ft.ListView(expand=True, spacing=10, padding=ft.Padding.only(left=20, right=20, bottom=20))
        self.empty_state = ft.Column(
            [
                ft.Icon(ft.Icons.QR_CODE_2, size=60, color=ft.Colors.GREY_400),
                ft.Text("No labels generated yet.", color=ft.Colors.GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        self.list_container = ft.Container(content=self.empty_state, expand=True)
        self.status_text = ft.Text(size=12, color=ft.Colors.GREY_700)

        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        self.container = ft.Column(
            [
                ft.Container(content=toolbar, padding=ft.Padding.only(left=20, right=20, top=10)),
                self.list_container,
                ft.Container(content=self.status_text, padding=ft.Padding.only(left=20, bottom=10)),
            ],
            expand=True,
        )

    def refresh(self):
        self.records = get_all_labels()
        self.selected_ids.clear()
        self.checkboxes.clear()
        self.select_all_checkbox.value = False
        self._update_selection_status()

        self.list_view.controls.clear()
        if not self.records:
            self.list_container.content = self.empty_state
            return

        for r in self.records:
            self.list_view.controls.append(self._build_row(r))
        self.list_container.content = self.list_view

    def _build_row(self, r: dict) -> ft.Control:
        asset_id = f"{r['asset_code']}-{r['asset_number']}"
        created = r["created_at"].replace("T", "  ") if r["created_at"] else ""

        checkbox = ft.Checkbox(
            value=False,
            on_change=lambda e, rid=r["id"]: self._on_row_check_change(rid, e.control.value),
        )
        self.checkboxes[r["id"]] = checkbox

        preview_path = r.get("label_path") or r["qr_image_path"]

        return ft.Container(
            content=ft.Row(
                [
                    checkbox,
                    ft.Image(src=preview_path, width=56, height=56, fit=ft.BoxFit.CONTAIN),
                    ft.Column(
                        [
                            ft.Text(asset_id, weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(r["department"], size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                r["description"] or "No description",
                                size=12, color=ft.Colors.GREY_600,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Text(created, size=11, color=ft.Colors.GREY_500),
                ],
                spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12, border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10, bgcolor=ft.Colors.WHITE,
        )

    def _on_row_check_change(self, record_id: int, checked: bool):
        if checked:
            self.selected_ids.add(record_id)
        else:
            self.selected_ids.discard(record_id)
            if self.select_all_checkbox.value:
                self.select_all_checkbox.value = False

        self._update_selection_status()
        self.page.update()

    def on_select_all_change(self, e):
        checked = self.select_all_checkbox.value
        self.selected_ids.clear()
        for record_id, checkbox in self.checkboxes.items():
            checkbox.value = checked
            if checked:
                self.selected_ids.add(record_id)

        self._update_selection_status()
        self.page.update()

    def _update_selection_status(self):
        count = len(self.selected_ids)
        self.selection_status.value = f"{count} selected"
        self.compile_btn.disabled = count == 0

    async def on_compile_click(self, e):
        if not self.selected_ids:
            return

        selected_records = [r for r in self.records if r["id"] in self.selected_ids]
        label_paths = [r.get("label_path") or r["qr_image_path"] for r in selected_records]

        try:
            pdf_path = compile_labels_to_pdf(label_paths)
            with open(pdf_path, "rb") as f:
                self.compiled_bytes = f.read()

            self.status_text.value = f"✅ Compiled {len(label_paths)} label(s). Choose where to save..."
            self.page.update()

            chosen_path = await self.file_picker.save_file(
                file_name="compiled_labels.pdf",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )

            if chosen_path:
                base, ext = os.path.splitext(chosen_path)
                if ext.lower() != ".pdf":
                    chosen_path = base + ".pdf"
                with open(chosen_path, "wb") as f:
                    f.write(self.compiled_bytes)
                self.status_text.value = f"📁 Compiled PDF saved at: {chosen_path}"
            else:
                self.status_text.value = "✅ Compiled PDF generated (not saved externally)."

        except Exception as ex:
            self.status_text.value = f"❌ Error compiling PDF: {str(ex)}"

        self.page.update()

    def get_view(self) -> ft.Control:
        self.refresh()
        return self.container