export function doTestModeHasEmptyAnswers() {
    const answersContainer = document.getElementById('answers_container');
    const buttons = answersContainer.querySelectorAll('input');
    const formattedAnswers = Array.from(buttons).map(element => element.checked);
    return !formattedAnswers.includes(true);
}

export async function processTestModeAnswers(roundInfo) {
    const answersContainer = document.getElementById('answers_container');
    const buttons = answersContainer.querySelectorAll('input');
    const pickedAnswer = Array.from(buttons)
        .filter(element => element.checked)
        .map(element => element.id)[0];

    const checkingResults = await fetch(
        'db/send_answers',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify( {answers: pickedAnswer} ),
        }
    ).then(response => response.json());

    const textTag = document.getElementById('bottom-div-round-text');
    const parts = roundInfo.round_text.split('___');

    // insert an <b> with correct answer into test text
    const correctAnswer = Object.keys(checkingResults.correct_answers)[0];
    const didIAnsweredCorrectly = checkingResults.correct_answers[correctAnswer]; 

    const underlineTextFull = document.createElement('b');
    const underlineText = document.createElement('u');
    underlineTextFull.appendChild(underlineText);
    
    underlineText.textContent = correctAnswer;
    underlineText.classList.add(didIAnsweredCorrectly ? 'green-underline' : 'red-underline');

    textTag.appendChild(document.createTextNode(parts[0]));
    textTag.appendChild(underlineTextFull);
    textTag.appendChild(document.createTextNode(parts[1]));

    const gotPointsText = document.getElementById('got-points-text');
    gotPointsText.textContent = `got points: ${checkingResults.got_points}/${checkingResults.max_points}`;

    return checkingResults.correct_answers;
}

export function setupTestMode(answers, round_text) {
    const answersContainer = document.getElementById('answers_container');
    const roundText = document.getElementById('round_text');

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

    roundText.textContent = round_text;
}