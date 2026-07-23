# Asset QR Code Generator

A desktop app for generating, tracking, and printing QR code asset labels. No installation required — just download, extract, and run.

## 📥 Downloading the App

1. Go to the project's **Releases** page on GitHub (usually found on the right-hand side of the repo page, or under the "Releases" tab).
2. Download the latest `.zip` file (e.g. `AssetQRApp.zip`).
3. Once downloaded, **extract the entire zip** to a folder of your choice (Desktop, Documents, wherever is convenient).

   > ⚠️ **Important:** Extract the whole zip, not just the `.exe` file inside it. The app needs its supporting files (DLLs, data folder) sitting in the same folder to run — it will not work if you copy only the `.exe` out on its own.

## ▶️ Running the App

1. Open the extracted folder.
2. Double-click **`Asset QR Code Generator.exe`** to launch the app.

   > If Windows shows a "Windows protected your PC" SmartScreen warning (common for apps not yet widely downloaded), click **More info** → **Run anyway**.

3. The app window will open — no installation, no admin rights, no Python needed.

## 🖥️ Using the App

### Generating a Label

1. On the **Home** screen, fill in:
   - **Department** (dropdown)
   - **Asset Code** and **Asset Number**
   - **Reference No.** and **Serial Number**
   - **Description**
2. Click **Generate QR Code**.
3. The QR label preview appears on the right. Every generated label is automatically saved to your local label library.
4. Optionally, toggle **"Save a copy elsewhere"** before generating to also save a copy of the PNG to a folder of your choice.

### Bulk Importing from Excel/CSV

1. Click **Import from Excel/CSV** near the top of the Home screen.
2. Select a `.csv` or `.xlsx` file containing your asset data. Column headers can be flexible (e.g. "Dept", "Department", "Asset No", "Asset Number" are all recognized).
3. A preview list shows every row found in the file:
   - Rows with all required info are checked and ready to generate.
   - Rows missing required info (Department, Asset Code, or Asset Number) are automatically unchecked and flagged — click the ✏️ **edit icon** on any row to fix it before generating.
4. Use **Select All** to select every valid row, or check/uncheck rows individually.
5. Click **Generate Selected** to batch-create labels for every checked row. A progress counter shows how many have been generated.

### Viewing & Managing Your Label Library (History)

Click the **History** icon in the top bar to open your label library.

- **Click any label's thumbnail** to view it enlarged, along with its full details.
- **Select labels** using the checkboxes, or use **Select All**.
- **Compile Selected to PDF** — choose a print size (1×1 in to 5×5 in) and compile your selected labels into a single, print-ready PDF, automatically paginated across standard A4 pages.
- **Delete** a single label using the 🗑️ icon on its row, or select multiple and click **Delete Selected**. Deleting removes the label permanently, including its image files — this cannot be undone, and you'll be asked to confirm first.

## ❓ Troubleshooting

| Issue | What to do |
|---|---|
| "Windows protected your PC" warning on launch | Click **More info** → **Run anyway**. This is expected for apps distributed outside the Microsoft Store. |
| Missing `.dll` error on launch | You likely moved only the `.exe` out of its folder. Re-extract the full zip and run the `.exe` from inside the complete extracted folder. |
| App won't open at all | Make sure you extracted the zip fully rather than trying to run it directly from inside the zip file/archive viewer. |
| Labels seem to have disappeared | Your label library is stored locally next to the app. If you moved/deleted the app folder, previously generated labels won't carry over — always keep the app in one consistent folder. |

## 🔒 Notes

- All label data and images are stored **locally on your computer** — nothing is uploaded anywhere.
- The app works fully offline.