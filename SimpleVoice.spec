# -*- mode: python ; coding: utf-8 -*-
"""
SimpleVoice - Configuración de PyInstaller
Archivo de especificación para crear ejecutable independiente
"""

import sys
import os
from pathlib import Path

# Configuraciones base
app_name = "SimpleVoice"
script_dir = Path.cwd()
src_dir = script_dir / "src"

# Archivos de datos a incluir
datas = []

# Intentar incluir archivos de CustomTkinter
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    datas.append((ctk_path, 'customtkinter'))
except ImportError:
    pass

# Imports ocultos (hidden imports)
hiddenimports = [
    'customtkinter',
    'pyaudio',
    'whisper',
    'pynput',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'threading',
    'logging',
    'tempfile',
    'wave',
    'numpy',
    'torch',
    'torchaudio',
    'transformers',
    'tokenizers',
    'regex',
    'ftfy',
    'more_itertools',
    'tiktoken',
    'triton',
    'openai',
    'datetime',
    'pathlib',
    'json',
    'subprocess',
    'shutil',
    'platform',
    'warnings',
    'typing'
]

# Módulos a excluir para reducir tamaño
excludes = [
    'matplotlib',
    'pandas',
    'scipy',
    'jupyter',
    'IPython',
    'notebook',
    'pytest',
    'setuptools',
    'distutils',
    'test',
    'unittest',
    'doctest',
    'pydoc',
    'tkinter.test',
    'lib2to3',
    'email',
    'html',
    'http',
    'urllib',
    'xml',
    'xmlrpc',
    'concurrent',
    'multiprocessing',
    'asyncio',
    'wsgiref',
    'plistlib',
    'uu',
    'base64',
    'binhex',
    'binascii',
    'quopri',
    'mimetypes',
    'mailbox',
    'mailcap',
    'smtplib',
    'poplib',
    'imaplib',
    'nntplib',
    'telnetlib',
    'ftplib',
    'netrc',
    'xdrlib',
    'uuid',
    'sqlite3',
    'dbm',
    'gdbm',
    'zipfile',
    'tarfile',
    'gzip',
    'bz2',
    'lzma',
    'zlib',
    'zipimport',
    'pkgutil',
    'modulefinder',
    'runpy',
    'compileall',
    'py_compile',
    'zipapp',
    'venv',
    'ensurepip',
    'ctypes.test',
    'tkinter.test',
    'idlelib',
    'turtle',
    'turtledemo'
]

# Análisis principal
a = Analysis(
    [str(src_dir / 'main_gui.py')],
    pathex=[str(script_dir), str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Filtrar archivos binarios innecesarios
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configurar ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir con UPX si está disponible
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola visible
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Aquí se puede añadir un icono .ico
    version=None,
    uac_admin=False,
    uac_uiaccess=False,
    windowed=True,  # Aplicación con ventana
)

# Para macOS - crear bundle .app
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{app_name}.app',
        icon=None,  # Aquí se puede añadir un icono .icns
        bundle_identifier=f'com.simplevoice.{app_name.lower()}',
        version='1.0.0',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'NSMicrophoneUsageDescription': 'SimpleVoice necesita acceso al micrófono para grabar audio y transcribir.',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'CFBundleExecutable': app_name,
            'CFBundleName': app_name,
            'CFBundleDisplayName': 'SimpleVoice',
            'CFBundleIdentifier': f'com.simplevoice.{app_name.lower()}',
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'SiVo',
            'LSMinimumSystemVersion': '10.15.0',
            'NSRequiresAquaSystemAppearance': 'False',
            'NSSupportsAutomaticGraphicsSwitching': 'True',
        },
    ) 