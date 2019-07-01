# -*- mode: python -*-

block_cipher = None


a = Analysis(['DockerCLI.py'],
             pathex=['/Users/artem/PycharmProjects/DockerCLI'],
             binaries=[],
             datas=[('DockerCLI.ui', 'DockerCLI.ui'), ('RunScriptWindow.ui', 'RunScriptWindow.ui'), ('resurse', 'resurse'), ('run_scripts', 'run_scripts')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='DockerCLI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DockerCLI')
app = BUNDLE(coll,
             name='DockerCLI.app',
             icon=None,
             bundle_identifier=None)
