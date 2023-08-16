# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['WOM/manage.py'],
    pathex=[],
    binaries=[],
    datas=[('WOM/App/*','App/'),('WOM/users/*','users/'),('WOM/users/templates/users/*','templates/users/'),('WOM/templates','templates/'),('WOM/App/static/*','static/App/')],
    hiddenimports=['matplotlib','pytz','simplejson','numpy','psycopg','Image','picklefield','plotly','whitenoise','pytest','whitenoise.middleware','whitenoise.storage','crispy_bootstrap4','django-crispy-forms','bootstrap4'],
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
    [],
    exclude_binaries=True,
    name='WOM',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WOM',
)
