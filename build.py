import os
import shutil

PYTHON_INTERPRETER_PATH = f'{os.getenv("localappdata")}/programs/python/python38/python.exe'
REQ_PACKAGES = ['nuitka==1.8.6']
EXE_ICON = ''  # allowed: png, ico
COPY_DIRS = ['tests', 'web']
COPY_FILES = []

#

for i in REQ_PACKAGES:
    os.system(f'{PYTHON_INTERPRETER_PATH} -m pip install {i}')

os.system(f'{PYTHON_INTERPRETER_PATH} -m nuitka --standalone {f"--windows-icon-from-ico {EXE_ICON}" if EXE_ICON else ""} main.py')

#

for i in COPY_DIRS:
    shutil.copytree(i, 'main.dist/')

for i in COPY_FILES:
    shutil.copy(i, 'main.dist/')
