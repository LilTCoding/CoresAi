
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Main GUI application
gui_analysis = Analysis(
    ['gui_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('dragon_logo.png', '.'),
        ('header_image.png', '.'),
        ('data', 'data'),
        ('models', 'models'),
        ('src', 'src'),
        ('production_ai_backend.py', '.'),
        ('test_ai_interface.html', '.'),
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
        'psutil',
        'wmi',
        'sounddevice',
        'soundfile',
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
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_pyz = PYZ(gui_analysis.pure, gui_analysis.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_analysis.scripts,
    [],
    exclude_binaries=True,
    name='CoresAI-GUI',
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
    icon='dragon_logo.png' if os.path.exists('dragon_logo.png') else None,
)

# Backend application
backend_analysis = Analysis(
    ['production_ai_backend.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('data', 'data'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests',
        'numpy',
        'psutil',
        'wmi',
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
        'pandas',
        'PyQt5',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

backend_pyz = PYZ(backend_analysis.pure, backend_analysis.zipped_data, cipher=block_cipher)

backend_exe = EXE(
    backend_pyz,
    backend_analysis.scripts,
    [],
    exclude_binaries=True,
    name='CoresAI-Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect everything into a distribution folder
coll = COLLECT(
    gui_exe,
    gui_analysis.binaries,
    gui_analysis.zipfiles,
    gui_analysis.datas,
    backend_exe,
    backend_analysis.binaries,
    backend_analysis.zipfiles,
    backend_analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CoresAI-Distribution',
)
