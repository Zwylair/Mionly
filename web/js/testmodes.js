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
    const answers = testInfo['randomize_answers'] ? shuffleArray(testInfo.answers) : testInfo.answers;

    if (testInfo['round_type'] == 'testmode') {
        const answersContainer = document.getElementById('answers_container');
        const testText = document.getElementById('test_text');

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

        testText.textContent = testInfo.round_text;
    }
    else if (testInfo['round_type'] == 'drag_testmode') {
        const textContainer = document.getElementById('test_text');
        const answersContainer = document.getElementById('answers_container');

        // spawn the target containers
        const parts = testInfo['round_text'].split('/');
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
        for (var answer of answers) {
            let answerDiv = document.createElement('div');
            Object.assign(answerDiv, { name: answer, className: 'draggable', draggable: true });
            let answerDivText = document.createElement('p');
            answerDivText.textContent = answer;
            answerDiv.appendChild(answerDivText);
            answersContainer.appendChild(answerDiv);
        }

        setDraggables();
    }

    const totalRoundsCount = await fetch('http://127.0.0.1:8000/db/get/total_rounds_count').then(response => response.json());
    const openedRoundsCount = await fetch('http://127.0.0.1:8000/db/get/opened_rounds_count').then(response => response.json());

    testTitle.textContent = testInfo.title;
    testCounter.textContent = `${openedRoundsCount}/${totalRoundsCount}`;
}

function setDraggables() {
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

async function sendSubmit() {
    const testInfo = await fetch('http://127.0.0.1:8000/db/get/round_info').then(response => response.json());
    const iconObject = document.createElement('img');
    iconObject.style = 'margin-right: 5px;';
    const button = document.getElementById('shaking-button');
    const bottomDiv = document.getElementById('bottom_div');
    let condition;

    if (testInfo['round_type'] == 'testmode') {
        const answersContainer = document.getElementById('answers_container');
        const buttons = answersContainer.querySelectorAll('input');
        condition = Array.from(buttons).map(element => element.checked);
    }
    else if (testInfo['round_type'] == 'drag_testmode') {
        const answersDivs = document.querySelectorAll('div#target');
        condition = Array.from(answersDivs).map(element => !!element.children.length);
    }

    if (!condition.includes(true)) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.disabled = true;

        let checkingResults;
        if (testInfo['round_type'] == 'testmode') {
            const answersContainer = document.getElementById('answers_container');
            const buttons = answersContainer.querySelectorAll('input');
            const pickedAnswer = Array.from(buttons)
                .filter(element => element.checked)
                .map(element => element.id)[0];

            checkingResults = await fetch(
                'http://127.0.0.1:8000/db/send_answers',
                {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify( {answers: pickedAnswer} ),
                }
            ).then(response => response.json());
        }
        else if (testInfo['round_type'] == 'drag_testmode') {
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
            checkingResults = await fetch(
                'http://127.0.0.1:8000/db/send_answers',
                {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify( {answers: answersList} ),
                }
            ).then(response => response.json());
        }

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
        bottomDiv.appendChild(bottomDivHeader);
        bottomDiv.classList.add(isAllRight ? 'green-border' : 'red-border');
        bottomDiv.classList.remove('hidden');

        // make a text with correct answers
        const textTag = document.createElement('pa');
        bottomDiv.appendChild(textTag);

        if (testInfo['round_type'] == 'testmode') {
            const parts = testInfo['round_text'].split('___');

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
        }
        else if (testInfo['round_type'] == 'drag_testmode') {
            const parts = testInfo['round_text'].split('/');

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
        }

        // "next" button
        const continueButton = document.createElement('button');
        const nextIconObject = document.createElement('img');
        nextIconObject.src = '/images/next.svg';
        continueButton.appendChild(nextIconObject);
        continueButton.classList.add('continue-button');
        continueButton.addEventListener('click', async () => {
            window.location.href = await fetch('http://127.0.0.1:8000/db/next_round').then(response => response.json());
        });
        bottomDiv.appendChild(continueButton);

        // if i remove hidden class and set the style at the same time, the transition won't work | 0.1s delay is not noticeable
        setTimeout(() => {
            audio.play();
            bottomDiv.style = 'transition: ease-out 0.5s; transform: translateY(-120px);';
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await updateTestInfo();

    const button = document.getElementById('shaking-button');
    button.addEventListener('animationend', () => { button.classList.remove('shake'); });
});
