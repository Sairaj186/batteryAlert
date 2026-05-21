# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['batteryalert.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['winshell', 'win32com', 'win32com.client', 'win32gui', 'win32api', 'win32con', 'winotify'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='batteryalert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
