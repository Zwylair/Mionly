async function updateTestInfo() {
    const testInfo = await eel.get_test_data()();

    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById("test_title");
    const testText = document.getElementById("test_text");
    const answersContainer = document.getElementById("answers_container");

    // get answers
    for (var answerObject of testInfo['answers']) {
        for (var key in answerObject) {
            answerText = key;
            isTrue = answerObject[key];
        }

        // make a container for answer radio button and label
        const answerDiv = document.createElement('div');
        answerDiv.classList = ['answer_div'];

        //  make answer elements
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'answerButton';
        radio.id = answerText;

        const label = document.createElement('label');
        label.textContent = answerText;

        answerDiv.appendChild(radio);
        answerDiv.appendChild(label);
        answersContainer.appendChild(answerDiv);
    }
    testTitle.textContent = testInfo['name'];
    testText.textContent = testInfo['test_text'];
    testCounter.textContent = `${await eel.get_completed_tests_count()() + 1}/${await eel.get_all_tests_count()()}`;
}

async function sendSubmit() {
    let answersContainer = document.getElementById("answers_container");
    let buttons = answersContainer.querySelectorAll('input');

    let radioButtonsIsChecked = [];
    buttons.forEach(element => {
        radioButtonsIsChecked.push(element.checked);
    });

    if (!radioButtonsIsChecked.includes(true)) {
        const button = document.getElementById('shaking-button');
        button.classList.add('shake');
    } else {
        const testInfo = await eel.get_test_data()();
        let pickedButtonIds = [];
        let answersList = [];

        buttons.forEach(element => {
            if (element.checked) {
                pickedButtonIds.push(element.id);
            }
        });

        for (var answerObject of testInfo['answers']) {
            for (var key in answerObject) {
                answerText = key;
                isTrue = answerObject[key];

                if (pickedButtonIds.includes(answerText)) {
                    answersList.push({answerText: isTrue})
                }
            }
        }

        await eel.submit_action(answersList)();
        window.location.href = await eel.load_next_test()();
    }
}


document.addEventListener('DOMContentLoaded', function() {
    updateTestInfo()

    const button = document.getElementById('shaking-button');

    button.addEventListener('animationend', function () {
        button.classList.remove('shake');
    });
});
