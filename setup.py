import os
import subprocess

icon_path = 'test_creator.data/images/icon.ico'
include_dirs = ['tests', 'web', 'test_creator.data']
include_files = []

subprocess.run('py -m pip install -r requirements.txt')

try:
    from cx_Freeze import setup, Executable
except ImportError:
    subprocess.run('py -m pip install cx_Freeze')
    from cx_Freeze import setup, Executable

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
    ],
    options={
        'build_exe': {
            'include_files': [f'{i}/' for i in include_dirs] + include_files
        }
    }
)

os.remove('build/exe.win-amd64-3.12/test_creator.data/test_creator.lock')
