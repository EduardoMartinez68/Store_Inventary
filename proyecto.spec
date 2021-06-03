# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['proyecto.py'],
             pathex=['C:\\Users\\eduar_000.EDUARDO\\Desktop\\py_inventari'],
             binaries=[],
             datas=[('mydatabase.db','.'),('mydatabaseClientes.db','.'),('mydatabaseCOMPRAS.db','.'),('mydatabaseHistorial.db','.'),('mydatabaseUsuarios.db','.'),('basura.png','.'),('carro.png','.'),('editar.png','.'),('enviar.png','.'),('escaner.png','.'),('historial.png','.'),('renvolso.png','.')],
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
          name='proyecto',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='proyecto')
