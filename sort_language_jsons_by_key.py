import os
import json

for i in os.listdir('languages'):
    lang: dict = json.load(open(f'languages/{i}', encoding='utf8'))
    json.dump(dict(sorted(lang.items())), open(f'languages/{i}', 'w', encoding='utf8'), ensure_ascii=False)
