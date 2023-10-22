import sqlite3
import eel
import settings

# import js-accessible funcs
import loader
import test_funcs

with sqlite3.connect(settings.SQL_DB_FN) as sql:
    cur = sql.cursor()
    for i in settings.SQL_CREATE_SEQUENCES:
        cur.execute(i)

    # if the previous test was completed by closing chrome, this will reset its progress to zero
    if cur.execute('SELECT * FROM storage').fetchone():
        cur.execute('DELETE FROM storage')

    if cur.execute('SELECT * FROM progress').fetchone():
        cur.execute('DELETE FROM progress')

eel.init(settings.EEL_WEB_DIR, allowed_extensions=['.js', '.html'])
eel.start('main.html', suppress_error=True, options=settings.EEL_OPTIONS)
