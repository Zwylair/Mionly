import eel
import settings


@eel.expose
def get_value_from_js(value: list):
    print(value, type(value))


eel.init(settings.EEL_WEB_DIR, allowed_extensions=['.js', '.html'])
eel.start('test.html', suppress_error=True, options=settings.EEL_OPTIONS)
