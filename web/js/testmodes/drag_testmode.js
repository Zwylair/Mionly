import { setupDragAndDrop } from '../setup_dnd.js';

export function doDragTestModeHasEmptyAnswers() {
    const answersDivs = document.querySelectorAll('div#target');
    const formattedAnswers = Array.from(answersDivs).map(element => !!element.children.length);
    return !formattedAnswers.includes(true);
}

export async function processDragTestModeAnswers(roundInfo) {
    const answersDivs = document.querySelectorAll('div#target');

    // collect my answers into dict['answerText': answerPosition]
    let answersList = {};
    let positionCount = 0;

    answersDivs.forEach(answerDiv => {
        positionCount += 1;
        const gotAnswerText = answerDiv.children[0].name;
        answersList[gotAnswerText] = positionCount;
    });

    // send answers
    const checkingResults = await fetch(
        'db/send_answers',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify( {answers: answersList} ),
        }
    ).then(response => response.json());

    const textTag = document.getElementById('bottom-div-round-text');
    const parts = roundInfo.round_text.split('___');

    // sort right answers by position
    var items = Object.keys(checkingResults.correct_answers).map((key) => [key, checkingResults.correct_answers[key]]);
    items.sort((first, second) => first[1] - second[1]);

    // insert right answers into bottomDiv text
    for (var rightData of items) {
        let [rightAnswer, isMyAnswerRight] = rightData;

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

export function setupDragTestMode(answers, round_text) {
    const textContainer = document.getElementById('round_text');
    const answersContainer = document.getElementById('answers_container');

    // spawn the target containers
    const parts = round_text.split('___');
    const textTag = document.createElement('pa');

    for (var part of parts.slice(0, parts.length - 1)) {
        // insert a <div> where you want to drag and drop the answer
        const targetAnswerContainer = document.createElement('div');
        targetAnswerContainer.id = 'target';

        textTag.appendChild(document.createTextNode(part));
        textTag.appendChild(targetAnswerContainer);
    }

    textTag.appendChild(document.createTextNode(parts[parts.length - 1]));
    textContainer.appendChild(textTag);

    // spawn the answers
    for (let answer of answers) {
        const answerDiv = document.createElement('div');
        answerDiv.name = answer;
        answerDiv.classList = 'draggable';
        answerDiv.draggable = true;

        const answerDivText = document.createElement('p');
        answerDivText.textContent = answer;

        answerDiv.appendChild(answerDivText);
        answersContainer.appendChild(answerDiv);
    }

    setupDragAndDrop();
}
