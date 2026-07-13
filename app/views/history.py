import os
import flet as ft
from app.data.database import get_all_labels
from app.controllers.qr_controller import delete_qr_code
from app.utils.batch_pdf_compiler import compile_labels_to_pdf

SIZE_OPTIONS = ["1", "2", "3", "4", "5"]


class HistoryView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.records: list[dict] = []
        self.selected_ids: set[int] = set()
        self.checkboxes: dict[int, ft.Checkbox] = {}
        self.compiled_bytes: bytes | None = None
        self._pending_delete_ids: list[int] = []

        self.select_all_checkbox = ft.Checkbox(
            label="Select All", value=False, on_change=self.on_select_all_change,
        )

        self.size_dropdown = ft.Dropdown(
            label="Size (in)",
            options=[ft.DropdownOption(s, text=f"{s}x{s}") for s in SIZE_OPTIONS],
            value="2",
            width=110,
        )

        self.compile_btn = ft.ElevatedButton(
            "Compile to PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self.on_compile_click,
            disabled=True,
        )
        self.delete_btn = ft.ElevatedButton(
            "Delete",
            icon=ft.Icons.DELETE,
            on_click=self.on_delete_click,
            disabled=True,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ft.Colors.WHITE,
                    ft.ControlState.DISABLED: ft.Colors.RED_200,
                },
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.RED,
                    ft.ControlState.DISABLED: ft.Colors.RED_50,
                },
                icon_color={
                    ft.ControlState.DEFAULT: ft.Colors.WHITE,
                    ft.ControlState.DISABLED: ft.Colors.RED_200,
                },
            ),
        )

        self.selection_status = ft.Text("0 selected", size=12, color=ft.Colors.GREY_600)

        toolbar = ft.Row(
            [
                self.select_all_checkbox,
                self.selection_status,
                ft.Container(expand=True),
                self.size_dropdown,
                self.compile_btn,
                self.delete_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.list_view = ft.ListView(expand=True, spacing=10, padding=ft.Padding.only(left=20, right=20, bottom=20))
        self.empty_state = ft.Column(
            [
                ft.Icon(ft.Icons.QR_CODE_2, size=60, color=ft.Colors.GREY_400),
                ft.Text("No QR codes generated yet.", color=ft.Colors.GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        )
        self.list_container = ft.Container(content=self.empty_state, expand=True, alignment=ft.Alignment.CENTER)
        self.status_text = ft.Text(size=12, color=ft.Colors.GREY_700)

        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        # --- Delete confirmation dialog --- #
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete QR code(s)?"),
            content=ft.Text("This will permanently remove the selected QR code(s) and their files. This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_delete),
                ft.TextButton("Delete", on_click=self._on_confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # --- Enlarged preview dialog --- #
        self.preview_image = ft.Image(src="", width=320, height=320, fit=ft.BoxFit.CONTAIN)
        self.preview_details = ft.Column(spacing=4)
        self.preview_dialog = ft.AlertDialog(
            modal=False,
            content=ft.Column(
                [self.preview_image, self.preview_details],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                spacing=12,
            ),
            actions=[ft.TextButton("Close", on_click=self._on_close_preview)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(self.confirm_dialog)
        self.page.overlay.append(self.preview_dialog)

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

        thumbnail = ft.Container(
            content=ft.Image(src=preview_path, width=56, height=56, fit=ft.BoxFit.CONTAIN),
            on_click=lambda e, rec=r: self._open_preview(rec),
            ink=True,
            border_radius=6,
        )

        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            tooltip="Delete this QR code",
            on_click=lambda e, rid=r["id"]: self._request_delete([rid]),
        )

        return ft.Container(
            content=ft.Row(
                [
                    checkbox,
                    thumbnail,
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
                    delete_btn,
                ],
                spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12, border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10, bgcolor=ft.Colors.WHITE,
        )

    def _open_preview(self, record: dict):
        asset_id = f"{record['asset_code']}-{record['asset_number']}"
        created = record["created_at"].replace("T", "  ") if record["created_at"] else ""
        preview_path = record.get("label_path") or record["qr_image_path"]

        self.preview_image.src = preview_path
        self.preview_details.controls = [
            ft.Text(asset_id, weight=ft.FontWeight.BOLD, size=18),
            ft.Text(f"Department: {record['department']}", size=13),
            ft.Text(f"Serial Number: {record['serial_number'] or 'N/A'}", size=13),
            ft.Text(f"Description: {record['description'] or 'No description'}", size=13),
            ft.Text(f"Generated: {created}", size=12, color=ft.Colors.GREY_500),
        ]
        self.preview_dialog.open = True
        self.page.update()

    def _on_close_preview(self, e):
        self.preview_dialog.open = False
        self.page.update()

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
        self.delete_btn.disabled = count == 0

    def on_delete_click(self, e):
        if self.selected_ids:
            self._request_delete(list(self.selected_ids))

    def _request_delete(self, ids: list[int]):
        if not ids:
            return
        self._pending_delete_ids = ids
        label = "QR code" if len(ids) == 1 else "QR codes"
        self.confirm_dialog.content = ft.Text(
            f"This will permanently remove {len(ids)} {label} and their files. This cannot be undone."
        )
        self.confirm_dialog.open = True
        self.page.update()

    def _on_cancel_delete(self, e):
        self._pending_delete_ids = []
        self.confirm_dialog.open = False
        self.page.update()

    def _on_confirm_delete(self, e):
        ids_to_delete = self._pending_delete_ids
        self._pending_delete_ids = []
        self.confirm_dialog.open = False

        deleted_count = 0
        for record_id in ids_to_delete:
            if delete_qr_code(record_id):
                deleted_count += 1

        self.status_text.value = f"🗑️ Deleted {deleted_count} QR code(s)."
        self.refresh()
        self.page.update()

    async def on_compile_click(self, e):
        if not self.selected_ids:
            return

        selected_records = [r for r in self.records if r["id"] in self.selected_ids]
        label_paths = [r.get("label_path") or r["qr_image_path"] for r in selected_records]
        label_size_in = float(self.size_dropdown.value or "2")

        try:
            pdf_path = compile_labels_to_pdf(label_paths, label_size_in=label_size_in)
            with open(pdf_path, "rb") as f:
                self.compiled_bytes = f.read()

            self.status_text.value = f"✅ Compiled {len(label_paths)} QR code(s) at {label_size_in}x{label_size_in}in. Choose where to save..."
            self.page.update()

            chosen_path = await self.file_picker.save_file(
                file_name="compiled_qr_codes.pdf",
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