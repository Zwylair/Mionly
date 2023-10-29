import json
import os
import base64
import rot1

for ww_book in os.listdir('tests/'):
    for unit in os.listdir(f'tests/{ww_book}/'):
        for test_dir in os.listdir(f'tests/{ww_book}/{unit}/'):
            for test_file in os.listdir(f'tests/{ww_book}/{unit}/{test_dir}'):
                with open(f'tests/{ww_book}/{unit}/{test_dir}/{test_file}') as file:
                    content = file.read()

                try:
                    content = json.loads(content)
                except BaseException:
                    print(f'already coded: {ww_book}/{unit}/{test_dir}/{test_file}')
                else:
                    print(f'processing: {ww_book}/{unit}/{test_dir}/{test_file}')
                    with open(f'tests/{ww_book}/{unit}/{test_dir}/{test_file}', 'w') as file:
                        file.write(rot1.rot1_encrypt(base64.b64encode(content.encode()).decode()))
