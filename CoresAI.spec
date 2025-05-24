# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\torey\\OneDrive\\Documents\\GitHub\\CoresAi\\gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('frontend/build', 'frontend/build'), ('*.json', '.'), ('*.png', '.'), ('*.ico', '.')],
    hiddenimports=['wmi', 'win32com.client', 'pythoncom', 'discord', 'pandas', 'numpy', 'PIL', 'requests', 'asyncio', 'aiohttp', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'psutil', 'ccxt', 'web3', 'eth_account', 'cryptography', 'redis', 'fastapi', 'uvicorn', 'websockets', 'schedule', 'hmac', 'hashlib', 'base64', 'json', 'time', 'datetime', 'threading', 'queue', 'logging', 'os', 'sys'],
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
    name='CoresAI',
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
    icon=['C:\\Users\\torey\\OneDrive\\Documents\\GitHub\\CoresAi\\coresai.ico'],
)
