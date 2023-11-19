import os.path
import shutil
import eel
import settings
import db

# import js-accessible funcs
import loader
import test_funcs
import rot1

db.wipe_storage()
if not os.path.exists('web/temp'):
	os.mkdir('web/temp')
shutil.rmtree('web/temp')
os.mkdir('web/temp')

eel.init(settings.EEL_WEB_DIR, allowed_extensions=['.js', '.html'])
eel.start('main.html', suppress_error=True, options=settings.EEL_OPTIONS)
