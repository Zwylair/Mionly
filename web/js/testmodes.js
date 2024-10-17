import { doTestModeHasEmptyAnswers, processTestModeAnswers, setupTestMode } from './testmodes/testmode.js';
import { doDragTestModeHasEmptyAnswers, processDragTestModeAnswers, setupDragTestMode } from './testmodes/drag_testmode.js';
import { doInputTestModeHasEmptyAnswers, processInputTestModeAnswers, setupInputTestMode } from './testmodes/input_testmode.js';

const roundTypeHandlers = {
    testmode: setupTestMode,
    drag_testmode: setupDragTestMode,
    input_testmode: setupInputTestMode,
};

const roundTypeEmptyAnswersHandlers = {
    testmode: doTestModeHasEmptyAnswers,
    drag_testmode: doDragTestModeHasEmptyAnswers,
    input_testmode: doInputTestModeHasEmptyAnswers,
};

const roundTypeAnswerProcessors = {
    testmode: processTestModeAnswers,
    drag_testmode: processDragTestModeAnswers,
    input_testmode: processInputTestModeAnswers,
};

function handleRoundType(roundType, answers, roundText) {
    const handler = roundTypeHandlers[roundType];

    if (handler) {
        handler(answers, roundText);
    } else {
        console.error(`No handler found for round type: ${roundType}`);
    }
}

function handleHasEmptyAnswers(roundType) {
    const handler = roundTypeEmptyAnswersHandlers[roundType];

    if (handler) {
        return handler();
    } else {
        console.error(`No empty answer handler found for round type: ${roundType}`);
    }
}

async function processAnswers(roundInfo) {
    const handler = roundTypeAnswerProcessors[roundInfo.round_type];

    if (handler) {
        return await handler(roundInfo);
    } else {
        console.error(`No answer processor found for round type: ${roundType}`);
    }
}

async function updateRoundInfo() {
    try {
        const isThisRoundAlreadyCompleted = await fetchJson('db/get/is_this_round_completed');

        if (isThisRoundAlreadyCompleted) {
            await nextRound();
            return;
        }

        const roundInfo = await fetchJson('db/get/round_info');
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
    const roundInfo = await fetchJson('db/get/round_info');
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
        iconObject.classList.add(isAllRight ? 'right-icon' : 'wrong-icon');

        // complete the bottom container
        const bottomDiv = document.getElementById('bottom_div');
        const bottomDivHeaderText = document.getElementById('bottom-div-title-text');
        bottomDivHeaderText.textContent = isAllRight ? 'Awesome!' : 'Incorrect';
        bottomDiv.classList.add(isAllRight ? 'green-border' : 'red-border');
        bottomDiv.classList.remove('hidden');

        // complete "next" button
        const nextIconObject = document.getElementById('continue-button-image');
        nextIconObject.classList.add('next-icon');

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

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

async function nextRound() {
    window.location.href = await fetchJson('db/next_round');
}

window.sendAnswers = sendAnswers;
window.nextRound = nextRound;

document.addEventListener('DOMContentLoaded', async () => {
    await updateRoundInfo();

    const button = document.getElementById('submit-button');
    button.addEventListener('animationend', () => { button.classList.remove('shake'); });
});
