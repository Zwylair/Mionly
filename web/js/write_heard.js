async function updateTestInfo() {
    const testInfo = await getTestData();
    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById('test_title');
    const hearButton = document.getElementById('hear_button');
  
    hearButton.addEventListener('click', () => {
        const audio = new Audio(testInfo.audio_path);
        audio.volume = 0.4;
        audio.play();
    });

    testTitle.textContent = testInfo.name;
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

    const answerContainer = document.getElementById('input_text_field');

    if (!answerContainer.value) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.setAttribute('disabled', 'disabled');

        // dump the progress
        let rightAnswer = await eel.submit_action(answerContainer.value)();

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

            // insert an <b> with correct answer into test text
            let underlineText = document.createElement('b');
            underlineText.textContent = rightAnswer;
            underlineText.classList.add('red-underline');

            bottomDiv.appendChild(underlineText);
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
