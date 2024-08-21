# -*- mode: python ; coding: utf-8 -*-

main = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
test_maker = Analysis(
    ['test_maker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

main_pyz = PYZ(main.pure)
test_maker_pyz = PYZ(test_maker.pure)

main_exe = EXE(
    main_pyz,
    main.scripts,
    [],
    exclude_binaries=True,
    name='Main',
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
    icon=['test_creator.data/icon.ico'],
)
test_maker_exe = EXE(
    test_maker_pyz,
    test_maker.scripts,
    [],
    exclude_binaries=True,
    name='Test maker',
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
    icon=['test_creator.data/icon.ico'],
)
test_maker_debug_exe = EXE(
    test_maker_pyz,
    test_maker.scripts,
    [],
    exclude_binaries=True,
    name='Test maker DEBUG',
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
    icon=['test_creator.data/icon.ico'],
)

main_coll = COLLECT(
    main_exe,
    main.binaries,
    main.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Main',
)
test_maker_coll = COLLECT(
    test_maker_exe,
    test_maker.binaries,
    test_maker.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Test maker',
)
test_maker_debug_coll = COLLECT(
    test_maker_debug_exe,
    test_maker.binaries,
    test_maker.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Test maker DEBUG',
)
