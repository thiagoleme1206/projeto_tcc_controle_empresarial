# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files
import os

block_cipher = None

additional_scripts = ['login.py', 'main.py', 'clientes.py', 'despesa.py', 'orcamento.py', 'projeto.py', 'receita.py']

a = Analysis(
    ['run.py'] + additional_scripts,
    pathex=[],
    binaries=[],
    datas=[
        *collect_data_files('psycopg2'),
        ('avllogo.ico', '.')  # Inclui o ícone explicitamente
    ],
    hiddenimports=[
        'messagebox._win32',
        'psycopg2',  # Adicione outras dependências ocultas aqui
        'tkinter',
        'PIL'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SistemaAVL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mantenha False para ocultar o console
    icon='avllogo.ico'
)