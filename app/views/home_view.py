import flet as ft
import os
from app.controllers.qr_controller import generate_and_compile

# --- Constants ---
DEPARTMENTS = [
    "HR",
    "PHILHEALTH",
    "IT",
    "FINANCE",
    "ADMIN",
    "OPERATIONS",
    "SALES",
]

ASSET_CODES = {
    "ASST": "Asset",
    "SUPP": "Supply",
    "EQP": "Equipment",
}


class HomeView:
    def __init__(self, page: ft.Page):
        self.page = page
        
        # --- 1. Department Dropdown ---
        self.department_dropdown = ft.Dropdown(
            label="Department",
            hint_text="Select department",
            options=[ft.dropdown.Option(d) for d in DEPARTMENTS],
            width=280,
            value="HR",
        )
        
        # --- 2. Asset Code Dropdown + Number ---
        self.asset_code_dropdown = ft.Dropdown(
            label="Asset Code",
            hint_text="Select type",
            options=[ft.dropdown.Option(code, text=name) for code, name in ASSET_CODES.items()],
            width=150,
            value="ASST",
        )
        
        self.asset_number_input = ft.TextField(
            label="Asset Number",
            hint_text="e.g., 001",
            width=120,
        )
        
        # --- 3. Serial Number ---
        self.serial_input = ft.TextField(
            label="Serial Number",
            hint_text="Enter serial number",
            width=280,
        )
        
        # --- 4. Description ---
        self.description_input = ft.TextField(
            label="Description",
            hint_text="e.g., Office Chair, Laptop, etc.",
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True,
        )
        
        # --- Generate Button & Preview ---
        self.generate_btn = ft.ElevatedButton(
            "Generate Asset Label & PDF",
            icon=ft.Icons.QR_CODE,   # This works on 0.85+
            on_click=self.on_generate_click,
            width=280,
            height=45,
        )
        
        # --- Status & Preview ---
        self.status_text = ft.Text(size=14, color=ft.Colors.GREY_700)  # Capital C!
        
        self.qr_preview = ft.Image(
            src="",                  # Explicit default src
            width=180,
            height=180,
            visible=False,
        )
        
        # --- File Picker (Modern setup) ---
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_picker_result
        self.page.overlay.append(self.file_picker)

        # --- Build Layout ---
        row1 = ft.Row(
            [
                self.department_dropdown,
                self.asset_code_dropdown,
                self.asset_number_input,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        )
        
        row2 = ft.Row(
            [self.serial_input],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        row3 = ft.Row(
            [self.description_input],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        row4 = ft.Row(
            [
                ft.Column(
                    [
                        self.generate_btn,
                        self.status_text,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(
                    content=self.qr_preview,
                    width=200,
                    height=200,
                    border=ft.border.all(1, ft.Colors.GREY_300),  # Capital C!
                    border_radius=10,
                    padding=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
        )

        self.content = ft.Column(
            [
                ft.Text("Asset QR Code Generator", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),  # Capital C!
                row1,
                row2,
                row3,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                row4,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def on_generate_click(self, e):
        """Validate inputs and generate the PDF."""
        if not self.department_dropdown.value:
            self.status_text.value = "⚠️ Please select a Department."
            self.page.update()
            return
        if not self.asset_number_input.value:
            self.status_text.value = "⚠️ Please enter an Asset Number."
            self.page.update()
            return

        try:
            pdf_path, img_path = generate_and_compile(
                department=self.department_dropdown.value,
                asset_code=self.asset_code_dropdown.value,
                asset_number=self.asset_number_input.value,
                serial_number=self.serial_input.value or "N/A",
                description=self.description_input.value or "No description provided",
            )

            self.qr_preview.src = img_path
            self.qr_preview.visible = True
            self.status_text.value = "✅ Asset label generated! Choose where to save..."

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            self.file_picker.save_file(
                file_name=f"asset_label_{self.asset_code_dropdown.value}_{self.asset_number_input.value}.pdf",
                bytes=pdf_bytes,
            )

            self.page.update()

        except Exception as ex:
            self.status_text.value = f"❌ Error: {str(ex)}"
            self.page.update()

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.status_text.value = f"📁 PDF saved at: {e.path}"
        else:
            self.status_text.value = "✅ PDF saved locally in the /outputs folder."
        self.page.update()

    def get_view(self):
        return self.content