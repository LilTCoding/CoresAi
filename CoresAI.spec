# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['gui_app.py'],  # Main application entry point
    pathex=['.'],
    binaries=[],
    datas=[
        ('dragon_logo.png', '.'),
        ('header_image.png', '.'),
        ('data', 'data'),
        ('models', 'models'),
        ('src', 'src'),
        ('*.json', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'requests',
        'pydantic',
        'numpy',
        'pandas',
        'discord',
        'asyncio',
        'aiohttp',
        'psutil',
        'wmi',
        'win32com.client',
        'pythoncom',
        'PIL',
        'tkinter',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'bark',
        'torch',
        'transformers',
        'tensorflow',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
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
    icon='dragon_logo.png' if os.path.exists('dragon_logo.png') else None,
)
