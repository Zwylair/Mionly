/**
 * @param {JSON} testInfo
 */
async function updateTestInfo() {
    const testInfo = await eel.get_test_data()();

    let testTitle = document.getElementById("test_title");
    let testText = document.getElementById("test_text");
    let answersContainer = document.getElementById("answers_container");

    // get answers
    for (var answerObject of testInfo['answers']) {
        for (var key in answerObject) {
            answerText = key;
            isTrue = answerObject[key];
        }

        // make a container for answer radio button and label
        let answerDiv = document.createElement('div');
        answerDiv.classList = ['answer_div'];

        //  make answer elements
        let radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'answerButton';
        radio.id = answerText;

        let label = document.createElement('label');
        label.textContent = answerText;

        answerDiv.appendChild(radio);
        answerDiv.appendChild(label);
        answersContainer.appendChild(answerDiv);
    }

    // update text and desc of test
    testTitle.textContent = testInfo['name'];
    testText.textContent = testInfo['test_text'];
}

async function sendSubmit() {
    let answersContainer = document.getElementById("answers_container");
    let buttons = answersContainer.querySelectorAll('input');

    let radioButtonsIsChecked = [];
    buttons.forEach(element => {
        radioButtonsIsChecked.push(element.checked);
    });

    if (!radioButtonsIsChecked.includes(true)) {
        alert('You arent picked any answer');
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

    // let testTitle = document.getElementById("test_title");
    // let testText = document.getElementById("test_text");
    // let answersContainer = document.getElementById("answers_container");

}


document.addEventListener('DOMContentLoaded', function() {
    updateTestInfo()
});
