import sys
import time
import ctypes
import winreg
import shutil
import threading
import subprocess
import webbrowser
import psutil
import colorama
import screeninfo
import dearpygui.dearpygui as dpg
import dearpygui_animate as animate
from test_creator.cyrillic_support import CyrillicSupport, FontPreset
from shared_funcs.language import loc, chosen_language
from shared_funcs.messageboxes import spawn_warning
from shared_funcs import language_picker, exit
from settings import *
import log

colorama.init(convert=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())
server_pid: int | None = None
server_env_key = 'mionly_server'.upper()
ALIVE_CHECK_TIMEOUT = 4


def check_and_create_association():
    extension = '.mionly'
    program_id = 'Zwylair.Mionly'
    description = 'Mionly Test File'
    executable_path = f'"{sys.executable}" "{__file__}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}"'
    run_command = f'{executable_path} "%1"'

    try:
        command = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, f'{program_id}\\shell\\open\\command')

        if command == run_command:
            logger.info(f'Association for {extension} already exists')
            return
    except FileNotFoundError:
        logger.info(f'No association found for {extension}. Creating now...')

    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            winreg.SetValue(key, '', winreg.REG_SZ, program_id)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, program_id) as key:
            winreg.SetValue(key, '', winreg.REG_SZ, description)

            with winreg.CreateKey(key, r'shell\open\command') as cmd_key:
                winreg.SetValue(cmd_key, '', winreg.REG_SZ, run_command)

        logger.info(f'Association for {extension} created successfully.')
    except Exception as e:
        logger.info(f'Failed to create association for {extension}: {e}')


def run_server():
    global server_pid

    check_for_running_server()
    if server_pid is not None:
        spawn_warning(loc('server.server_is_already_running'))
        return

    # ['.../executable.exe', 'path/to/test_file/test.mionly']
    args = []
    if len(sys.argv[1:]) > 0:
        logger.info(f'Run options: {sys.argv[1:]}')
        args = sys.argv[1:]
        # open_browser()  # browser should be opened from server/runner.py

    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags = 1
    startup_info.wShowWindow = 0
    run_args = (['server.exe'] if getattr(sys, 'frozen', False) else [sys.executable, 'server/runner.py']) + args
    server_process = subprocess.Popen(run_args, startupinfo=startup_info, env=(dict(os.environ) | {server_env_key: "yes"}))
    server_pid = server_process.pid
    dpg.set_value('server__server_status', loc('server.running'))

    if len(args) == 0:
        open_browser()


def stop_server():
    global server_pid

    if server_pid is None:
        spawn_warning(loc('server.server_is_not_running'))
        logger.info('Server is not running')
        return

    for proc in psutil.process_iter(['pid']):
        if proc.info.get('pid') == server_pid:
            try:
                proc.terminate()
                logger.info(f'Server (PID: {server_pid}) was terminated')
                dpg.set_value('server__server_status', loc('server.off'))
            except psutil.NoSuchProcess:
                logger.info(f'Process was finished before i did it (PID: {server_pid})')
            except psutil.AccessDenied:
                logger.info(f'Have no permission to terminate server process (PID: {server_pid})')


def check_for_running_server():
    global server_pid

    if psutil.pid_exists(-1 if server_pid is None else server_pid):
        return

    for proc in psutil.process_iter(['pid', 'environ']):
        if proc.info.get('environ') is None:
            continue

        if server_env_key in proc.info.get('environ'):
            logger.info(f'Found ran mionly server with pid {proc.info.get("pid")}')
            server_pid = proc.info.get('pid')
            return
    server_pid = None


def alive_checker():
    while True:
        check_for_running_server()
        dpg.set_value(
            'server__server_status',
            loc('server.off' if server_pid is None else 'server.running')
        )
        time.sleep(ALIVE_CHECK_TIMEOUT)


def open_browser():
    webbrowser.open_new('http://{}:{}/index.html'.format(HOST_URL, HOST_PORT))


if __name__ == '__main__':
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logger.info('Ran not as admin, rerunning')

        mionly_args = sys.argv[1:]
        arguments = [__file__] + mionly_args
        arguments = ' '.join(['"' + i + '"' for i in arguments])
        arguments = (mionly_args if mionly_args else None) if getattr(sys, 'frozen', False) else arguments

        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, arguments, None, 1)
        sys.exit(0)

    logger.info('Ran as admin')

    # moving to main directory (changes when opened by test file)
    os.chdir(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__))
    shutil.rmtree(WEB_CACHE_PATH, ignore_errors=True)
    os.makedirs(WEB_CACHE_PATH, exist_ok=True)
    check_and_create_association()
    check_for_running_server()

    # set up gui
    monitor = screeninfo.get_monitors()[0]
    monitor_size = (monitor.width, monitor.height)
    viewport_size = (600, 400)

    dpg.create_context()
    # dpg_dnd.initialize()
    dpg.create_viewport(
        title='Mionly v2.0: server', large_icon=os.path.join(SHARED_FOLDER_PATH, 'images/icon.ico'),
        width=viewport_size[0], height=viewport_size[1],
        x_pos=int(monitor_size[0] / 2 - viewport_size[0] / 2),
        y_pos=int(monitor_size[1] / 2 - viewport_size[1] / 2)
    )

    with dpg.value_registry():
        dpg.add_string_value(tag='server__server_status', default_value=loc('server.off'))
        dpg.add_string_value(tag='shared__picked_lang', default_value=chosen_language)

    with dpg.font_registry():
        CyrillicSupport(
            FontPreset(
                path=os.path.join(SHARED_FOLDER_PATH, 'fonts/nunito/Nunito-Regular.ttf'),
                size=24, id='nunito', bind_font_as_default=True
            )
        )

    logger.debug('Loading textures')
    width, height, channels, data = dpg.load_image(os.path.join(SHARED_FOLDER_PATH, 'images/language.png'))
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag='texture__language')

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 7, category=dpg.mvThemeCat_Core)

        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (168, 168, 168), category=dpg.mvThemeCat_Core)

    dpg.bind_theme(global_theme)

    with dpg.window(no_title_bar=True, no_resize=True, no_close=True, no_move=True) as window:
        dpg.add_image_button(
            texture_tag='texture__language', width=32, height=32, pos=[dpg.get_viewport_width() - 64, 7],
            tag='shared__language_button',
            callback=lambda: language_picker.open_languages_window()
        )

        with dpg.group(horizontal=True):
            dpg.add_button(label=loc('server.run_server'), callback=run_server)
            dpg.add_button(label=loc('server.stop_server'), callback=stop_server)
            dpg.add_button(label=loc('server.open_browser'), callback=open_browser)

        with dpg.group(horizontal=True, horizontal_spacing=7):
            dpg.add_text(loc('server.server_status_label'))
            dpg.add_text(source='server__server_status')

        dpg.add_separator()

    dpg.set_primary_window(window, True)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    if len(sys.argv[1:]) > 0:
        run_server()

    alive_checker_thread = threading.Thread(target=alive_checker, daemon=True)
    setup_exit_thread = threading.Thread(
        target=lambda: exit.setup(__file__, SERVER_LOCK_FILENAME),
        daemon=True
    )
    setup_exit_thread.start()
    alive_checker_thread.start()

    while dpg.is_dearpygui_running():
        animate.run()
        dpg.render_dearpygui_frame()
    exit.stop_mionly()
    check_for_running_server()

    if psutil.pid_exists(server_pid):
        for process in psutil.process_iter(['pid']):
            try:
                if process.pid == server_pid: process.terminate()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                break
