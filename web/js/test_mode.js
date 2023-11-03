async function updateTestInfo() {
    const testInfo = await getTestData();
    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById('test_title');
    const testText = document.getElementById('test_text');
    const answersContainer = document.getElementById('answers_container');

    // get answers
    const answers = shuffleArray(Object.keys(testInfo.answers));
    for (var answerText of answers) {
        // make a container for answer radio button and label
        const answerDiv = document.createElement('div');
        answerDiv.classList = ['answer_div'];

        // make answer elements
        const radio = document.createElement('input');
        Object.assign(radio, { type: 'radio', name: 'answerButton', id: answerText });

        const label = document.createElement('label');
        label.textContent = answerText;

        answerDiv.appendChild(radio);
        answerDiv.appendChild(label);
        answersContainer.appendChild(answerDiv);
    }

    testTitle.textContent = testInfo.name;
    testText.textContent = testInfo.test_text;
    testCounter.textContent = `${await eel.get_all_tests_count()() - await eel.get_available_tests_count()()}/${await eel.get_all_tests_count()()}`;
}

async function sendSubmit() {
    const rightIcon = document.createElement('span');
    rightIcon.classList.add('material-symbols-outlined');
    rightIcon.textContent = 'task_alt';

    const wrongIcon = document.createElement('span');
    wrongIcon.classList.add('material-symbols-outlined');
    wrongIcon.textContent = 'dangerous';

    //

    const button = document.getElementById('shaking-button');
    const bottomDiv = document.getElementById('bottomDiv');

    let answersContainer = document.getElementById('answers_container');
    let buttons = answersContainer.querySelectorAll('input');
    let radioButtonsIsChecked = Array.from(buttons).map(element => element.checked);

    if (!radioButtonsIsChecked.includes(true) && !blockSubmit) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.setAttribute('disabled', 'disabled');

        const testInfo = await getTestData();
        let answer = {};

        // get ids (answerText) of checked buttons
        const pickedButtonIds = Array.from(buttons)
            .filter(element => element.checked)
            .map(element => element.id);

        // get original answers by given ids
        for (const answerText of Object.keys(testInfo.answers)) {
            if (pickedButtonIds.includes(answerText)) {
                answer[answerText] = testInfo.answers[answerText];
            }
        }

        // dump the progress
        let rightAnswer = await eel.submit_action(answer)();

        const audio = new Audio(`sounds/${rightAnswer === null ? 'right' : 'wrong'}.mp3`);
        audio.volume = 0.4;

        // prepare the bottomDiv
        const bottomDivTitle = document.createElement('div');
        const bottomDivTitleText = document.createElement('h3');

        // header template
        bottomDivTitle.classList.add('bottom-div-titlebox');
        bottomDivTitle.appendChild(rightAnswer === null ? rightIcon : wrongIcon)
        bottomDivTitle.appendChild(bottomDivTitleText);

        // show the bottomDiv
        bottomDiv.classList.remove('hidden');

        console.log(rightAnswer)
        if (rightAnswer === null) {
            bottomDiv.classList.add('green-border');

            // complete the header
            bottomDivTitleText.textContent = 'Awesome!';
            bottomDiv.appendChild(bottomDivTitle);
        } else {
            bottomDiv.classList.add('red-border');

            // complete the header
            bottomDivTitleText.textContent = 'Incorrect';
            bottomDiv.appendChild(bottomDivTitle);

            // make a text with correct answers
            const parts = testInfo['test_text'].split('___');
            const textTag = document.createElement('pa');

            // insert an <b> with correct answer into test text
            let underlineText = document.createElement('b');
            underlineText.textContent = Object.keys(rightAnswer)[0];
            underlineText.classList.add('red-underline');

            textTag.appendChild(document.createTextNode(parts[0]));
            textTag.appendChild(underlineText);
            textTag.appendChild(document.createTextNode(parts[1]));

            bottomDiv.appendChild(textTag);
        }

        // "next" button
        const continueButton = document.createElement('button');
        continueButton.textContent = '➤';
        continueButton.classList.add('continue-button');
        continueButton.addEventListener('click', async function() { window.location.href = await eel.load_next_test()(); });
        bottomDiv.appendChild(continueButton);

        // if i remove hidden class and set the style at the same time, the transition won't work | 0.1s delay is not noticeable
        setTimeout(function() {
            audio.play();
            bottomDiv.style = 'transition: ease-out 0.5s; transform: translateY(-120px);';
        }, 100);
    }
}


document.addEventListener('DOMContentLoaded', function() {
    updateTestInfo()

    const button = document.getElementById('shaking-button');

    button.addEventListener('animationend', function () {
        button.classList.remove('shake');
    });
});
