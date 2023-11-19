from datetime import datetime
import os
import time
import shutil
import psutil
import subprocess

PYTHON_INTERPRETER_PATH = f'{os.getenv("localappdata")}/programs/python/python38/python.exe'
REQ_PACKAGES = ['nuitka==1.8.6']
EXE_ICON = 'web/favicon.ico'  # allowed: png, ico
ALLOW_CONSOLE = False
COPY_DIRS = ['tests', 'web']
COPY_FILES = []

#

for i in REQ_PACKAGES:
    os.system(f'{PYTHON_INTERPRETER_PATH} -m pip install {i}')

args = [
    '--standalone',
    f'--windows-icon-from-ico={EXE_ICON}' if EXE_ICON else '',
    '' if ALLOW_CONSOLE else '--disable-console'
]
subprocess.Popen(f'cmd /c start cmd /c {PYTHON_INTERPRETER_PATH} -m nuitka {" ".join([i for i in args if i])} main.py')
made_time = datetime.now().strftime('%H:%M:%S')

# wait for a while to make sure cmd is started
time.sleep(2)

for proc in psutil.process_iter(['pid', 'name']):
    proc_made_time = datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')

    if proc_made_time == made_time and proc.name() == 'cmd.exe':
        while True:
            try:
                proc.status()
                time.sleep(1)
            except psutil.NoSuchProcess:
                print('building finished. copying additional files')
                break

#

for i in COPY_DIRS:
    shutil.copytree(i, f'main.dist/{i}')

for i in COPY_FILES:
    shutil.copy(i, f'main.dist/{i}')

print('done')
