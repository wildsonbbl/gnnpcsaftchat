# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import copy_metadata

datas = [
    ("./chat/templates", "./chat/templates"),
    ("./productionfiles", "./productionfiles"),

]
datas += copy_metadata("django-bootstrap-v5")
runtime_hooks = []
if os.environ.get("GNNPCSAFTCHAT_RTCOMPAT"):
    runtime_hooks.append("./hooks/runtime-rtcompat.py")


a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["tiktoken_ext.openai_public", "tiktoken_ext", "linkify-it-py"],
    hookspath=["./hooks"],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="gnnpcsaftchat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["electron/icon.ico"],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="gnnpcsaftchat",
)
