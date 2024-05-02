# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['check_for_gale.py'],
    pathex=[],
    binaries=[],
    datas=[('create_satellite_file.py', '.'), ('Sounds\\french_gale.mp3', 'Sounds'), ('Sounds\\greek_gale.mp3', 'Sounds'), ('wind_icon.png', '.')],
    hiddenimports=[],
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
    name='check_for_gale',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['wind_icon.png'],
)
