async function updateTestInfo() {
    const isThisRoundAlreadyCompleted = await fetch(
        'http://127.0.0.1:8000/db/get/is_this_round_completed'
    ).then(response => response.json());

    if (isThisRoundAlreadyCompleted) {
        window.location.href = await fetch('http://127.0.0.1:8000/db/next_round').then(response => response.json());
    }

    const testInfo = await fetch('http://127.0.0.1:8000/db/get/round_info').then(response => response.json());
    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById('test_title');
    const testText = document.getElementById('test_text');
    const answersContainer = document.getElementById('answers_container');
    const answers = testInfo.randomize_answers ? shuffleArray(testInfo.answers) : testInfo.answers;

    answers.forEach(element => {
        // make a container for answer radio button and label
        const answerDiv = document.createElement('div');
        answerDiv.classList = ['answer_div'];

        // make answer elements
        const radio = document.createElement('input');
        Object.assign(radio, { type: 'radio', name: 'answerButton', id: element });

        const label = document.createElement('label');
        label.textContent = element;

        answerDiv.appendChild(radio);
        answerDiv.appendChild(label);
        answersContainer.appendChild(answerDiv);
    });

    const totalRoundsCount = await fetch('http://127.0.0.1:8000/db/get/total_rounds_count').then(response => response.json());
    const openedRoundsCount = await fetch('http://127.0.0.1:8000/db/get/opened_rounds_count').then(response => response.json());

    testTitle.textContent = testInfo.title;
    testText.textContent = testInfo.round_text;
    testCounter.textContent = `${openedRoundsCount}/${totalRoundsCount}`;
}

async function sendSubmit() {
    const testInfo = await fetch('http://127.0.0.1:8000/db/get/round_info').then(response => response.json());
    const iconObject = document.createElement('img');
    iconObject.style = 'margin-right: 7px;';
    const button = document.getElementById('shaking-button');
    const bottomDiv = document.getElementById('bottomDiv');

    let answersContainer = document.getElementById('answers_container');
    let buttons = answersContainer.querySelectorAll('input');
    let radioButtonsIsChecked = Array.from(buttons).map(element => element.checked);

    if (!radioButtonsIsChecked.includes(true)) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.disabled = true;

        const pickedAnswer = Array.from(buttons)
            .filter(element => element.checked)
            .map(element => element.id)[0];

        let checkingResults = await fetch(
            'http://127.0.0.1:8000/db/send_answers',
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify( {answers: pickedAnswer} ),
            }
        ).then(response => response.json());

        const isAllRight = !Object.values(checkingResults).includes(false);
        const audio = new Audio(isAllRight ? '/sounds/right.mp3' : '/sounds/wrong.mp3');
        iconObject.src = isAllRight ? '/images/right.svg' : '/images/wrong.svg';
        audio.volume = 0.4;

        // prepare the bottom container
        const bottomDivHeader = document.createElement('div');
        const bottomDivHeaderText = document.createElement('h3');
        bottomDivHeaderText.textContent = isAllRight ? 'Awesome!' : 'Incorrect';
        bottomDivHeader.classList.add('bottom-div-titlebox');
        bottomDivHeader.appendChild(iconObject);
        bottomDivHeader.appendChild(bottomDivHeaderText);
        bottomDiv.classList.add(isAllRight ? 'green-border' : 'red-border');
        bottomDiv.appendChild(bottomDivHeader);
        bottomDiv.classList.remove('hidden');

        // make a text with correct answers
        const parts = testInfo['round_text'].split('___');
        const textTag = document.createElement('pa');

        // insert an <b> with correct answer into test text
        const correctAnswer = Object.keys(checkingResults)[0];
        const didIAnsweredCorrectly = checkingResults[correctAnswer]; 

        const underlineText = document.createElement('b');
        underlineText.textContent = correctAnswer;
        underlineText.classList.add(didIAnsweredCorrectly ? 'green-underline' : 'red-underline');

        textTag.appendChild(document.createTextNode(parts[0]));
        textTag.appendChild(underlineText);
        textTag.appendChild(document.createTextNode(parts[1]));

        bottomDiv.appendChild(textTag);

        // "next" button
        const continueButton = document.createElement('button');
        continueButton.textContent = '➤';
        continueButton.classList.add('continue-button');
        continueButton.addEventListener('click', async () => {
            window.location.href = await fetch('http://127.0.0.1:8000/db/next_round').then(response => response.json());
        });
        bottomDiv.appendChild(continueButton);

        // if i remove hidden class and set the style at the same time, the transition won't work | 0.01s delay is not noticeable
        setTimeout(() => {
            audio.play();
            bottomDiv.style = 'transition: ease-out 0.5s; transform: translateY(-120px);';
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateTestInfo();

    const button = document.getElementById('shaking-button');
    button.addEventListener('animationend', () => { button.classList.remove('shake'); });
});
