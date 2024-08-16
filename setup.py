import shutil
import subprocess

dirs = ['tests', 'web', 'languages']
files = ['icon.ico']

shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

subprocess.run('py -m pip install -r requirements.txt')
subprocess.run('py -m pip install pyinstaller')
subprocess.run('pyinstaller setup.spec')

shutil.copytree('dist/Test maker/', f'dist/Main/', dirs_exist_ok=True)
shutil.rmtree('dist/Test maker', ignore_errors=True)

for directory in dirs:
    shutil.copytree(directory, f'dist/Main/{directory}', dirs_exist_ok=True)

for file in files:
    shutil.copy(file, f'dist/Main/{file}')
