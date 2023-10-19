import eel
import settings

eel.init(settings.EEL_WEB_DIR, allowed_extensions=['.js', '.html'])


@eel.expose
def func_from_py(text_to_say: str):
    print(text_to_say)


eel.func_from_js('it was called from python!')


eel.start('main.html', suppress_error=True, options=settings.EEL_OPTIONS)
