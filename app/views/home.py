import os
import flet as ft
from app.controllers.qr_controller import generate_and_compile
from app.models.asset_config import DEPARTMENTS, ASSET_CODE_MAPPING
from app.utils.import_parser import parse_import_file


class HomeView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.label_bytes = None

        # --- Form fields --- #
        self.department_dropdown = ft.Dropdown(
            label="Department",
            hint_text="Select department",
            leading_icon=ft.Icons.APARTMENT,
            options=[ft.DropdownOption(d) for d in DEPARTMENTS],
            expand=True,
        )

        self.reference_no = ft.TextField(
            label="Reference No.",
            hint_text="Reference Number",
            prefix_icon=ft.Icons.TAG,
            expand=True,
        ) 

        self.asset_code_dropdown = ft.Dropdown(
            label="Asset Code",
            hint_text="Type",
            leading_icon=ft.Icons.CATEGORY,
            options=[ft.DropdownOption(code, text=name) for code, name in ASSET_CODE_MAPPING.items()],
            width=170,
        )

        self.asset_number_input = ft.TextField(
            label="Asset Number",
            hint_text="e.g., 001",
            prefix_icon=ft.Icons.TAG,
            expand=True,
        )

        self.serial_input = ft.TextField(
            label="Serial Number",
            hint_text="Enter serial number",
            prefix_icon=ft.Icons.QR_CODE_2,
            expand=True,
        )

        self.description_input = ft.TextField(
            label="Description",
            hint_text="e.g., Office Chair, Laptop, etc.",
            prefix_icon=ft.Icons.DESCRIPTION,
            multiline=True,
            min_lines=1,
            max_lines=4,
            expand=True,
        )

        # --- Optional save toggle --- #
        self.save_copy_switch = ft.Switch(value=False)
        save_copy_row = ft.Row(
            [
                self.save_copy_switch,
                ft.Column(
                    [
                        ft.Text("Save a copy elsewhere", size=13, weight=ft.FontWeight.W_500),
                        ft.Text(
                            "Otherwise it's just kept in your library.",
                            size=11,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        )

        # --- Generate button & status --- #
        self.generate_btn = ft.ElevatedButton(
            "Generate QR Code",
            icon=ft.Icons.QR_CODE,
            on_click=self.on_generate_click,
            height=45,
            width=280,
        )

        self.status_text = ft.Text(size=13, color=ft.Colors.GREY_700)

        # --- QR preview --- #
        self.qr_preview = ft.Image(
            src="",
            width=150,
            height=150,
            fit=ft.BoxFit.CONTAIN,
            visible=False,
        )
        self.empty_preview = ft.Column(
            [
                ft.Icon(ft.Icons.QR_CODE_2, size=48, color=ft.Colors.GREY_400),
                ft.Text("Preview", size=12, color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )
        self.preview_container = ft.Container(
            content=ft.Stack([self.empty_preview, self.qr_preview], alignment=ft.Alignment.CENTER),
            width=190,
            height=190,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            alignment=ft.Alignment.CENTER,
        )

        # --- File Picker --- #
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        # --- Import from Excel/CSV --- #
        self.import_file_picker = ft.FilePicker()
        self.page.services.append(self.import_file_picker)

        self.imported_rows: list[dict] = []
        self.import_row_checkboxes: dict[int, ft.Checkbox] = {}

        self.import_btn = ft.OutlinedButton(
            "Import from Excel/CSV",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_import_click,
        )

        self.import_select_all = ft.Checkbox(value=True, on_change=self._on_import_select_all_change)
        self.import_list_view = ft.ListView(spacing=6, height=280)
        self.import_status = ft.Text(size=12, color=ft.Colors.GREY_700)
        self.import_generate_btn = ft.ElevatedButton(
            "Generate Selected",
            icon=ft.Icons.QR_CODE,
            on_click=self.on_import_generate_click,
        )

        self.import_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Import Preview"),
            content=ft.Column(
                [
                    ft.Row([self.import_select_all, ft.Text("Select All", size=13)]),
                    ft.Divider(height=4),
                    self.import_list_view,
                    self.import_status,
                ],
                tight=True,
                spacing=8,
                width=420,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_import_cancel),
                self.import_generate_btn,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.import_dialog)

        # --- Edit imported row dialog --- #
        self._editing_row_index: int | None = None

        self.edit_department = ft.TextField(label="Department")
        self.edit_asset_code = ft.TextField(label="Asset Code", width=170)
        self.edit_asset_number = ft.TextField(label="Asset Number", expand=True)
        self.edit_reference_no = ft.TextField(label="Reference No.")
        self.edit_serial_number = ft.TextField(label="Serial Number")
        self.edit_description = ft.TextField(label="Description", multiline=True, min_lines=1, max_lines=3)

        self.edit_row_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Row"),
            content=ft.Column(
                [
                    self.edit_department,
                    ft.Row([self.edit_asset_code, self.edit_asset_number], spacing=12),
                    self.edit_reference_no,
                    self.edit_serial_number,
                    self.edit_description,
                ],
                tight=True, spacing=12, width=380,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_edit_row_cancel),
                ft.ElevatedButton("Save", on_click=self._on_edit_row_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.edit_row_dialog)

        # --- Layout: form card (left) + actions/preview card (right) --- #
        form_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Asset Information", size=15, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            self.import_btn,
                        ],
                    ),
                    self.department_dropdown,
                    ft.Row([self.asset_code_dropdown, self.asset_number_input], spacing=12),
                    ft.Row([self.reference_no, self.serial_input], spacing=12),
                    ft.Divider(height=12),
                    self.description_input,
                ],
                spacing=14,
            ),
            padding=20,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            expand=3,
        )

        actions_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("QR Preview", size=15, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=12),
                    ft.Row([self.preview_container], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    save_copy_row,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.generate_btn,
                    self.status_text,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            expand=2,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row([form_card, actions_card], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
                ],
            ),
            padding=24,
        )

    def _clear_form(self):
        self.reference_no.value = ""
        self.asset_number_input.value = ""
        self.serial_input.value = ""
        self.description_input.value = ""

    def _set_status(self, message: str):
        self.status_text.value = message
        self.page.update()

    async def on_generate_click(self, e):
        if not self.department_dropdown.value:
            self._set_status("⚠️ Please select a Department.")
            return
        if not self.asset_number_input.value:
            self._set_status("⚠️ Please enter an Asset Number.")
            return

        try:
            label_path, img_path, record_id = generate_and_compile(
                department=self.department_dropdown.value,
                reference_no=self.reference_no.value or "N/A",
                asset_code=self.asset_code_dropdown.value,
                asset_number=self.asset_number_input.value,
                serial_number=self.serial_input.value or "N/A",
                description=self.description_input.value or "No description provided",
            )

            with open(label_path, "rb") as f:
                self.label_bytes = f.read()

            self.qr_preview.src = img_path
            self.qr_preview.visible = True
            self.empty_preview.visible = False

            if self.save_copy_switch.value:
                self._set_status("✅ QR generated! Choose where to save a copy...")
                self.page.update()

                chosen_path = await self.file_picker.save_file(
                    file_name=f"{self.asset_code_dropdown.value}_{self.asset_number_input.value}.png",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["png"],
                )

                if chosen_path:
                        # Force the correct extension regardless of what the user typed/edited
                        base, ext = os.path.splitext(chosen_path)
                        if ext.lower() != ".png":
                            chosen_path = base + ".png"

                        with open(chosen_path, "wb") as f:
                            f.write(self.label_bytes)
                        self._set_status(f"📁 Copy saved at: {chosen_path}")
                else:
                    self._set_status("✅ Saved to your label library only.")
            else:
                self._set_status(f"✅ QR generated and saved to your library.")

            self._clear_form()
            self.page.update()

        except Exception as ex:
            self._set_status(f"❌ Error: {str(ex)}")

    def get_view(self):
        return self.content
    
    async def on_import_click(self, e):
        files = await self.import_file_picker.pick_files(
            dialog_title="Select an Excel or CSV file",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx", "xls", "csv"],
            allow_multiple=False,
        )

        if not files:
            return

        try:
            self.imported_rows = parse_import_file(files[0].path)
        except Exception as ex:
            self._set_status(f"❌ Import error: {str(ex)}")
            return

        if not self.imported_rows:
            self._set_status("⚠️ No rows found in the selected file.")
            return

        self._build_import_preview()
        self.import_dialog.open = True
        self.page.update()

    def _build_import_preview(self):
        self.import_row_checkboxes.clear()
        self.import_list_view.controls.clear()
        self.import_select_all.value = True

        for idx, row in enumerate(self.imported_rows):
            is_valid = not row["missing_fields"]
            checkbox = ft.Checkbox(value=is_valid, disabled=not is_valid)
            self.import_row_checkboxes[idx] = checkbox

            summary = f"{row['department'] or '—'} / {row['asset_code'] or '—'}-{row['asset_number'] or '—'}"
            desc = row["description"] or "No description"

            if is_valid:
                detail_color = ft.Colors.GREY_700
                warning = None
            else:
                detail_color = ft.Colors.RED_400
                warning = ft.Text(
                    f"Row {row['row_number']}: missing {', '.join(row['missing_fields'])}",
                    size=11, color=ft.Colors.RED_400,
                )

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_size=18,
                tooltip="Edit this row",
                on_click=lambda e, i=idx: self._open_edit_row(i),
            )

            row_controls = [
                ft.Row(
                    [
                        checkbox,
                        ft.Column(
                            [
                                ft.Text(summary, size=13, weight=ft.FontWeight.W_500, color=detail_color),
                                ft.Text(desc, size=11, color=ft.Colors.GREY_500, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=0, expand=True,
                        ),
                        edit_btn,
                    ],
                    spacing=8,
                ),
            ]
            if warning:
                row_controls.append(warning)

            self.import_list_view.controls.append(
                ft.Container(
                    content=ft.Column(row_controls, spacing=2),
                    padding=8, border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=8,
                )
            )

        valid_count = sum(1 for r in self.imported_rows if not r["missing_fields"])
        invalid_count = len(self.imported_rows) - valid_count
        self.import_status.value = f"{valid_count} ready, {invalid_count} skipped (missing required fields)"

    def _on_import_select_all_change(self, e):
        checked = self.import_select_all.value
        for idx, checkbox in self.import_row_checkboxes.items():
            if not checkbox.disabled:  # never auto-check invalid rows
                checkbox.value = checked
        self.page.update()

    def _on_import_cancel(self, e):
        self.import_dialog.open = False
        self.page.update()

    def _open_edit_row(self, idx: int):
        row = self.imported_rows[idx]
        self._editing_row_index = idx

        self.edit_department.value = row["department"]
        self.edit_asset_code.value = row["asset_code"]
        self.edit_asset_number.value = row["asset_number"]
        self.edit_reference_no.value = row["reference_no"]
        self.edit_serial_number.value = row["serial_number"]
        self.edit_description.value = row["description"]

        self.edit_row_dialog.open = True
        self.page.update()

    def _on_edit_row_cancel(self, e):
        self._editing_row_index = None
        self.edit_row_dialog.open = False
        self.page.update()

    def _on_edit_row_save(self, e):
        idx = self._editing_row_index
        if idx is None:
            return

        row = self.imported_rows[idx]
        row["department"] = (self.edit_department.value or "").strip()
        row["asset_code"] = (self.edit_asset_code.value or "").strip()
        row["asset_number"] = (self.edit_asset_number.value or "").strip()
        row["reference_no"] = (self.edit_reference_no.value or "").strip()
        row["serial_number"] = (self.edit_serial_number.value or "").strip()
        row["description"] = (self.edit_description.value or "").strip()

        row["missing_fields"] = [
            f for f in ("department", "asset_code", "asset_number") if not row[f]
        ]

        self._editing_row_index = None
        self.edit_row_dialog.open = False
        self._build_import_preview()
        self.page.update()

    async def on_import_generate_click(self, e):
        selected_indices = [
            idx for idx, checkbox in self.import_row_checkboxes.items()
            if checkbox.value and not checkbox.disabled
        ]

        if not selected_indices:
            self.import_status.value = "⚠️ No rows selected."
            self.page.update()
            return

        self.import_generate_btn.disabled = True
        total = len(selected_indices)
        success_count = 0
        failed_rows = []

        for position, idx in enumerate(selected_indices, start=1):
            row = self.imported_rows[idx]

            self.import_status.value = f"⏳ Generating {position} of {total}... ({success_count} succeeded, {len(failed_rows)} failed)"
            self.page.update()

            try:
                generate_and_compile(
                    department=row["department"],
                    reference_no=row["reference_no"] or "N/A",
                    asset_code=row["asset_code"],
                    asset_number=row["asset_number"],
                    serial_number=row["serial_number"] or "N/A",
                    description=row["description"] or "No description provided",
                )
                success_count += 1
            except Exception as ex:
                failed_rows.append((row["row_number"], str(ex)))

        self.import_dialog.open = False
        self.imported_rows = []
        self.import_row_checkboxes.clear()
        self.import_generate_btn.disabled = False

        if failed_rows:
            failed_summary = "; ".join(f"row {rn}: {msg}" for rn, msg in failed_rows[:3])
            more = f" (+{len(failed_rows) - 3} more)" if len(failed_rows) > 3 else ""
            self._set_status(f"✅ Generated {success_count}. ❌ {len(failed_rows)} failed — {failed_summary}{more}")
        else:
            self._set_status(f"✅ Generated {success_count} label(s) from import.")

        self.page.update()