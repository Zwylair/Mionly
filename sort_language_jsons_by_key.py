import json
from settings import *

root_dir = os.path.join(SHARED_FOLDER_PATH, 'languages')

for i in os.listdir(root_dir):
    lang: dict = json.load(open(os.path.join(root_dir, i), encoding='utf8'))
    json.dump(
        dict(sorted(lang.items())), open(os.path.join(root_dir, i), 'w', encoding='utf8'),
        ensure_ascii=False,
        indent=2
    )
