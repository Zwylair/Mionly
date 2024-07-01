from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app

setup(
    name='Mionly',
    version='2.0.0',
    description='',
    executables=[
        Executable('main.py'),
        Executable('test_creator.py', base='Win32GUI'),
    ],
)
