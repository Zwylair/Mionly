import os
import shutil
import subprocess

include_dirs = ['tests', 'web', 'test_creator.data']
include_files = []

shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

subprocess.run('py -m pip install -r requirements.txt')
subprocess.run('py -m pip install pyinstaller')
subprocess.run('pyinstaller setup.spec')

for i in os.listdir('dist'):
    if i == 'Main':
        continue

    shutil.copytree(f'dist/{i}/', f'dist/Main/', dirs_exist_ok=True)
    shutil.rmtree(f'dist/{i}', ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)

for directory in include_dirs:
    shutil.copytree(directory, f'dist/Main/{directory}', dirs_exist_ok=True)

for file in include_files:
    shutil.copy(file, f'dist/Main/{file}')
