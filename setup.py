from cx_Freeze import setup, Executable
from settings import *

icon_path = 'test_creator.data/images/icon.ico'
include_dirs = ['tests', 'web', SHARED_FOLDER_PATH]
include_files = []

setup(
    author='Zwylair',
    description='Mionly',
    name='Mionly',
    version='2.0',
    executables=[
        Executable('main.py', icon=icon_path, target_name='Mionly', base='Win32GUI'),
        Executable('main.py', icon=icon_path, target_name='Mionly DEBUG'),
        Executable('test_maker.py', icon=icon_path, target_name='Test maker', base='Win32GUI'),
        Executable('test_maker.py', icon=icon_path, target_name='Test maker DEBUG'),
        Executable('server/runner.py', target_name='server'),
    ],
    options={
        'build_exe': {
            'include_files': [f'{i}/' for i in include_dirs] + include_files,
            'packages': ['uvicorn'],
        }
    }
)

if os.path.exists('build/exe.win-amd64-3.12/test_creator.data/test_creator.lock'):
    os.remove('build/exe.win-amd64-3.12/test_creator.data/test_creator.lock')
