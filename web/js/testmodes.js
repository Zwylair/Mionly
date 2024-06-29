const roundTypeHandlers = {
    testmode: setupTestMode,
    drag_testmode: setupDragTestMode,
};

const roundTypeEmptyAnswersHandlers = {
    testmode: doTestModeHasEmptyAnswers,
    drag_testmode: doDragTestModeHasEmptyAnswers,
};

const roundTypeAnswerProcessors = {
    testmode: processTestModeAnswers,
    drag_testmode: processDragTestModeAnswers,
};

function handleRoundType(roundType, answers, roundText) {
    const handler = roundTypeHandlers[roundType];

    if (handler) {
        handler(answers, roundText);
    } else {
        console.error(`No handler found for round type: ${roundType}`);
    }
}

function setupTestMode(answers, round_text) {
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

function setupDragTestMode(answers, round_text) {
    const textContainer = document.getElementById('round_text');
    const answersContainer = document.getElementById('answers_container');

    // spawn the target containers
    const parts = round_text.split('/');
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

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

function handleHasEmptyAnswers(roundType) {
    const handler = roundTypeEmptyAnswersHandlers[roundType];

    if (handler) {
        return handler();
    } else {
        console.error(`No empty answer handler found for round type: ${roundType}`);
    }
}

function doTestModeHasEmptyAnswers() {
    const answersContainer = document.getElementById('answers_container');
    const buttons = answersContainer.querySelectorAll('input');
    const formattedAnswers = Array.from(buttons).map(element => element.checked);
    return !formattedAnswers.includes(true);
}

function doDragTestModeHasEmptyAnswers() {
    const answersDivs = document.querySelectorAll('div#target');
    const formattedAnswers = Array.from(answersDivs).map(element => !!element.children.length);
    return !formattedAnswers.includes(true);
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

async function processAnswers(roundInfo) {
    const handler = roundTypeAnswerProcessors[roundInfo.round_type];

    if (handler) {
        return await handler(roundInfo);
    } else {
        console.error(`No answer processor found for round type: ${roundType}`);
    }
}

async function processTestModeAnswers(roundInfo) {
    const answersContainer = document.getElementById('answers_container');
    const buttons = answersContainer.querySelectorAll('input');
    const pickedAnswer = Array.from(buttons)
        .filter(element => element.checked)
        .map(element => element.id)[0];

    const checkingResults = await fetch(
        'http://127.0.0.1:8000/db/send_answers',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify( {answers: pickedAnswer} ),
        }
    ).then(response => response.json());

    const textTag = document.getElementById('bottom-div-round-text');
    const parts = roundInfo.round_text.split('___');

    // insert an <b> with correct answer into test text
    const correctAnswer = Object.keys(checkingResults)[0];
    const didIAnsweredCorrectly = checkingResults[correctAnswer]; 

    const underlineTextFull = document.createElement('b');
    const underlineText = document.createElement('u');
    underlineTextFull.appendChild(underlineText);
    
    underlineText.textContent = correctAnswer;
    underlineText.classList.add(didIAnsweredCorrectly ? 'green-underline' : 'red-underline');

    textTag.appendChild(document.createTextNode(parts[0]));
    textTag.appendChild(underlineTextFull);
    textTag.appendChild(document.createTextNode(parts[1]));

    return checkingResults;
}

async function processDragTestModeAnswers(roundInfo) {
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
        'http://127.0.0.1:8000/db/send_answers',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify( {answers: answersList} ),
        }
    ).then(response => response.json());

    const textTag = document.getElementById('bottom-div-round-text');
    const parts = roundInfo.round_text.split('/');

    // sort right answers by position
    var items = Object.keys(checkingResults).map((key) => [key, checkingResults[key]]);
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

    return checkingResults;
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

async function updateRoundInfo() {
    try {
        const isThisRoundAlreadyCompleted = await fetchJson('http://127.0.0.1:8000/db/get/is_this_round_completed');

        if (isThisRoundAlreadyCompleted) {
            await nextRound();
            return;
        }

        const roundInfo = await fetchJson('http://127.0.0.1:8000/db/get/round_info');
        const roundCounter = document.getElementById('round_counter');
        const roundTitle = document.getElementById('round_title');
        const answers = roundInfo.randomize_answers ? shuffleArray(roundInfo.answers) : roundInfo.answers;

        handleRoundType(roundInfo.round_type, answers, roundInfo.round_text);

        roundTitle.textContent = roundInfo.title;
        roundCounter.textContent = roundInfo.round_counter_text;
    } catch (error) {
        console.error('Failed to update round info:', error);
    }
}

async function sendAnswers() {
    const roundInfo = await fetchJson('http://127.0.0.1:8000/db/get/round_info');
    const button = document.getElementById('submit-button');

    if (handleHasEmptyAnswers(roundInfo.round_type)) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.disabled = true;

        const checkingResults = await processAnswers(roundInfo);
        const isAllRight = !Object.values(checkingResults).includes(false);
        const audio = new Audio(isAllRight ? '/sounds/right.mp3' : '/sounds/wrong.mp3');
        audio.volume = 0.4;

        const iconObject = document.getElementById('bottom-div-title-icon');
        iconObject.src = isAllRight ? '/images/right.svg' : '/images/wrong.svg';

        // complete the bottom container
        const bottomDiv = document.getElementById('bottom_div');
        const bottomDivHeaderText = document.getElementById('bottom-div-title-text');
        bottomDivHeaderText.textContent = isAllRight ? 'Awesome!' : 'Incorrect';
        bottomDiv.classList.add(isAllRight ? 'green-border' : 'red-border');
        bottomDiv.classList.remove('hidden');

        // complete "next" button
        const nextIconObject = document.getElementById('continue-button-image');
        nextIconObject.src = '/images/next.svg';

        // if i remove hidden class and set the style at the same time, the transition won't work | 0.1s delay is not noticeable
        setTimeout(() => {
            audio.play();
            bottomDiv.style = 'transition: ease-out 0.5s; transform: translateY(-120px);';
        }, 100);
    }
}

async function fetchJson(url) {
    const response = await fetch(url);
    return response.json();
}

async function nextRound() {
    window.location.href = await fetchJson('http://127.0.0.1:8000/db/next_round');
}

function setupDragAndDrop() {
    const draggables = document.querySelectorAll('.draggable');
    const container = document.querySelector('.container-box');
    const targets = document.querySelectorAll('div#target');
    let draggableWidths = [];

    // some magic
    draggables.forEach(draggable => {
        draggableWidths.push(draggable.offsetWidth);
        draggable.addEventListener('dragstart', () => draggable.classList.add('dragging'));
        draggable.addEventListener('dragend', () => draggable.classList.remove('dragging'));
    });

    container.addEventListener('dragover', e => { e.preventDefault(); });
    container.addEventListener('drop', () => {
        const draggable = document.querySelector('.dragging');

        container.appendChild(draggable);
        draggable.classList.remove('dragging');
    });

    targets.forEach(target => {
        target.addEventListener('dragover', e => { e.preventDefault(); });
        target.addEventListener('drop', () => {
            if (target.children.length === 0) {
                const draggable = document.querySelector('.dragging');

                target.appendChild(draggable);
                draggable.classList.remove('dragging');
            }
        });

        // set target container width to the longest answer width
        target.style.minWidth = `${Math.max(...draggableWidths) + 15}px`;
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    await updateRoundInfo();

    const button = document.getElementById('submit-button');
    button.addEventListener('animationend', () => { button.classList.remove('shake'); });
});
