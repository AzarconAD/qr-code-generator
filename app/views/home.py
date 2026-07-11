import flet as ft
from app.controllers.qr_controller import generate_and_compile
from app.models.asset_config import DEPARTMENTS, ASSET_CODE_MAPPING


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
                            "Otherwise it's just kept in your label library.",
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
            "Generate Label",
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

        # --- Layout: form card (left) + actions/preview card (right) --- #
        form_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Asset Information", size=15, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=12),
                    self.department_dropdown,
                    ft.Row([self.asset_code_dropdown, self.asset_number_input], spacing=12),
                    self.serial_input,
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
                    with open(chosen_path, "wb") as f:
                        f.write(self.label_bytes)
                    self._set_status(f"📁 Copy saved at: {chosen_path}")
                else:
                    self._set_status("✅ Saved to your QR library only.")
            else:
                self._set_status(f"✅ QR generated and saved to your library.")

            self._clear_form()
            self.page.update()

        except Exception as ex:
            self._set_status(f"❌ Error: {str(ex)}")

    def get_view(self):
        return self.content