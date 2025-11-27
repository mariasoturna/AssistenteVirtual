# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Coletar arquivos extras do safehttpx e groovy
safehttpx_path = r"C:\Users\mariaelrb\AppData\Local\Programs\Python\Python312\Lib\site-packages\safehttpx"
groovy_path = r"C:\Users\mariaelrb\AppData\Local\Programs\Python\Python312\Lib\site-packages\groovy"

safehttpx_datas = [(os.path.join(safehttpx_path, "version.txt"), "safehttpx")]
groovy_datas = [(os.path.join(groovy_path, "version.txt"), "groovy")]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=safehttpx_datas + groovy_datas,
    hiddenimports=[],
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
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True
)