# -*- mode: python ; coding: utf-8 -*-
# FileSyncTool.spec  —  PyInstaller build spec

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ── Collect pywebview data files (JS bridge, etc.) ──
webview_datas = collect_data_files("webview")

# ── Collect google-api-python-client discovery files ──
google_datas = (
    collect_data_files("googleapiclient")
    + collect_data_files("google.auth")
    + collect_data_files("google.oauth2")
)

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        # Bundle the entire web_GUI folder
        ("web_GUI", "web_GUI"),
        # pywebview internal assets
        *webview_datas,
        # Google API client discovery JSON files
        *google_datas,
    ],
    hiddenimports=[
        # pywebview Windows backend
        "webview.platforms.winforms",
        "clr",
        "pythonnet",
        # Google auth stack
        "google.auth.transport.requests",
        "google.oauth2.credentials",
        "google_auth_oauthlib.flow",
        "googleapiclient.discovery",
        "googleapiclient.http",
        "googleapiclient.errors",
        # HTTP transport used by google-auth
        "httplib2",
        "uritemplate",
        "cachetools",
        "pyasn1",
        "pyasn1_modules",
        "rsa",
        # Other potential hidden imports
        "bottle",
        "proxy_tools",
    ] + collect_submodules("googleapiclient"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FileSyncTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # Set True if UPX is installed and you want smaller size
    console=False,       # Windowed — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="web_GUI/icon.ico",  # Uncomment and set path if you have an icon
    onefile=True,
)
