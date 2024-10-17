export function doInputTestModeHasEmptyAnswers() {
    const inputFields = document.querySelectorAll('input');
    const formattedAnswers = Array.from(inputFields).map(e => e.value === '');
    return !formattedAnswers.includes(false);
}

export async function processInputTestModeAnswers(roundInfo) {
    const inputFields = document.querySelectorAll('input');
    const writtenAnswers = Array.from(inputFields).map(element => element.value);
    const checkingResults = await fetch(
        'db/send_answers',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify( {answers: writtenAnswers} ),
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

    // insert right answers into bottomDiv text
    for (var rightAnswer in checkingResults.correct_answers) {
        let isMyAnswerRight = checkingResults.correct_answers[rightAnswer];

        // spawn underlined text
        const targetAnswerContainerFull = document.createElement('b');
        const targetAnswerContainer = document.createElement('u');
        targetAnswerContainerFull.appendChild(targetAnswerContainer);
        targetAnswerContainer.textContent = rightAnswer;
        targetAnswerContainer.classList.add(isMyAnswerRight ? 'green-underline' : 'red-underline');

        textTag.appendChild(document.createTextNode(parts[0]));
        textTag.appendChild(targetAnswerContainerFull);
        parts.shift();
    }
    textTag.appendChild(document.createTextNode(parts[0]));

    const gotPointsText = document.getElementById('got-points-text');
    gotPointsText.textContent = `got points: ${checkingResults.got_points}/${checkingResults.max_points}`;

    return checkingResults.correct_answers;
}

export function setupInputTestMode(answers, round_text) {
    const textContainer = document.getElementById('round_text');

    // spawn the target containers
    const parts = round_text.split('___');
    const textTag = document.createElement('pa');

    for (var part of parts.slice(0, parts.length - 1)) {
        // insert a <ipnut type="text"> where you want to drag and drop the answer
        const answerContainer = document.createElement('input');
        Object.assign(answerContainer, { type: 'text' });

        textTag.appendChild(document.createTextNode(part));
        textTag.appendChild(answerContainer);
    }

    textTag.appendChild(document.createTextNode(parts[parts.length - 1]));
    textContainer.appendChild(textTag);
}
