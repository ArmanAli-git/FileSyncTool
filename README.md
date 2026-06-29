# ⚡ File Sync Tool

**Stop manually copying files. Let it sync.**

A lightweight, snappy desktop app that keeps two local folders — or a local folder and Google Drive — perfectly in sync. Built with a modern animated GUI, no subscriptions, no cloud lock-in.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![pywebview](https://img.shields.io/badge/GUI-pywebview-5C6BC0?style=flat-square)](https://pywebview.flowrl.com/)
[![Google Drive](https://img.shields.io/badge/Cloud-Google%20Drive-4285F4?style=flat-square&logo=googledrive&logoColor=white)](https://drive.google.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

---

## ✨ Features & Interface

- 📁 **Local ↔ Local Sync:** Sync any two folders on your machine or across drives.
- ☁️ **Local ↔ Google Drive:** Sync a local folder with a Google Drive folder.
- 🧠 **Smart Sync:** Compares modification times to only copy changed files without blindly overwriting.
- 🎨 **Modern GUI:** Built with HTML/CSS/JS via pywebview, featuring smooth animations, bouncy card-based folder selection, inline cloud auth, and a dynamic progress bar.
- 📦 **Single EXE:** No dependencies required. Just download and run.

---

## ☁️ Google Drive Setup (Optional)

To sync with Google Drive, you'll need a free personal API token to connect your app to your Drive.

1. **Create a Project:** Go to the [Google Cloud Console](https://console.cloud.google.com) and create a new project.
2. **Enable the API:** In the left menu, go to **APIs & Services > Library**, search for **Google Drive API**, and click **Enable**.
3. **OAuth Consent Screen:**
   - Go to **APIs & Services > OAuth consent screen**.
   - Choose **External** and click Create. Fill in the required app name and email fields.
   - **Crucial:** Under **Test users**, add your own Google email address.
4. **Create Credentials:**
   - Go to **APIs & Services > Credentials**.
   - Click **+ Create Credentials > OAuth client ID**.
   - Select **Desktop app** as the application type and create.
5. **Download and Rename:** Download the resulting JSON file, rename it exactly to **`credentials.json`**, and place it in the same folder as `FileSyncTool.exe`.
6. **First Run:** Open the app, toggle **Cloud** on, and log in via the browser popup. A `token.json` will be saved next to the EXE for future use.

_(Skip this if you only need local-to-local sync!)_

---

## 📖 How to Use

### Local Sync

1. Run `FileSyncTool.exe`.
2. Click **Location A** and **Location B** to select your folders.
3. Keep the **Cloud** toggle **OFF**, and click **Sync**.

### Cloud Sync

1. Run `FileSyncTool.exe`.
2. Select your local folder as **Location A**.
3. Toggle **Cloud** ON (requires `credentials.json` setup above).
4. Select or create a Google Drive folder, and click **Sync**.

---

## ⚠️ Limitations

This is a **manual, on-demand** sync tool — not a background service. It doesn't watch your folders or sync automatically. You open it, hit Sync, done.

A few things to keep in mind:

- **Newer file wins.** No conflict resolution UI — whichever file was modified more recently gets copied over. Keep your system clock accurate.
- **Deletions don't propagate.** If you delete a file in one location, it stays in the other. This is intentional — the tool is additive only, it never removes anything.
- **Google-native files are skipped.** Google Docs, Sheets, Slides, etc. have no real file to download, so they're ignored during cloud sync.
- **One folder pair at a time.** Open another instance if you need to sync multiple pairs.

---

## 🏗️ How It's Built

**Tech Stack:** Python 3.12, pywebview, google-api-python-client, PyInstaller.

```text
FileSyncTool/
├── main.py          # App entry point, pywebview window, sync logic
├── Cloud.py         # Google Drive API engine
├── web_GUI/         # UI structure, styling, JS bridge, and local fonts
├── credentials.json # Your Google API token (stays local)
├── token.json       # Auto-generated auth token (stays local)
└── FileSyncTool.spec # PyInstaller build spec
```

---

## 🔒 Privacy & Security

- **Your credentials never leave your machine.** `credentials.json` and `token.json` are local files only.
- The app requests the `drive.file` scope — it can **only access files it creates or that you explicitly open with it**.
- No telemetry or analytics.

---

## 🔨 Build from Source

```bash
pip install pyinstaller
python -m PyInstaller FileSyncTool.spec --distpath .dist --workpath .dist/build --noconfirm
```

---

## 📄 License

MIT

---

<div align="center">
Made with ☕ and a frustration for manual file copying.
</div>
