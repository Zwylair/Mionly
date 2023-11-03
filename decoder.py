import json
import os
import base64
import rot1

for ww_book in os.listdir('tests/'):
    for unit in os.listdir(f'tests/{ww_book}/'):
        for test_dir in os.listdir(f'tests/{ww_book}/{unit}/'):
            for root, dirs, files in os.walk(f'tests/{ww_book}/{unit}/{test_dir}'):
                for file in files:
                    with open(f'{root}/{file}') as f:
                        content = f.read()

                    try:
                        json.loads(content)
                    except BaseException:
                        print(f'processing: {root}/{file}')

                        with open(f'{root}/{file}', 'w') as f:
                            f.write(base64.b64decode(rot1.rot1_decrypt(content).encode()).decode())
                    else:
                        print(f'already decoded: {root}/{file}')
