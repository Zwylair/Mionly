import json
import os
import base64
import rot1

available_tests = []
for ww_book in os.listdir('tests/'):  # stairs, my favourite part of code 😋
    for unit in os.listdir(f'tests/{ww_book}/'):
        for test_dir in os.listdir(f'tests/{ww_book}/{unit}/'):
            for root, dirs, _ in os.walk(f'tests/{ww_book}/{unit}/{test_dir}'):
                for test_type in dirs:
                    if test_type == 'write_heard':
                        for file in os.listdir(f'tests/{ww_book}/{unit}/{test_dir}/{test_type}'):
                            available_tests.append(f'{root}/{test_type}/{file}')

#

mp3_files = [i for i in os.listdir() if i.endswith('.mp3')]
mp3_nums = [i + 1 for i in range(len(mp3_files))]
av_nums = [i + 1 for i in range(len(available_tests))]
while True:
    picked_test, picked_mp3 = '', ''

    while picked_test not in available_tests:
        for i, j in zip(av_nums, available_tests):
            print(f'[{i}] -- {j}')

        picked_test = available_tests[int(input('\nChoose the test: ')) - 1]

    print('\n\n')

    while picked_mp3 not in mp3_files:
        for i, j in zip(mp3_nums, mp3_files):
            print(f'[{i}] -- {j}')

        picked_mp3 = mp3_files[int(input('\nChoose the mp3 file to encode: ')) - 1]

    #

    with open(picked_test) as f:
        content = f.read()

    with open(picked_mp3, 'rb') as f:
        audio_content = f.read()

    try:
        content = json.loads(content)
        is_decoded = True
    except BaseException:
        content = json.loads(base64.b64decode(rot1.rot1_decrypt(content).encode()).decode())
        is_decoded = False

    content['coded_audio'] = base64.b64encode(audio_content).decode()
    content = json.dumps(content)

    with open(picked_test, 'w') as file:
        if is_decoded:
            file.write(content)
        else:
            file.write(rot1.rot1_encrypt(base64.b64encode(content.encode()).decode()))

    print('\n\nDone\n\n')
