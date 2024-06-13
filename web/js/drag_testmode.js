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
    const textContainer = document.getElementById('testTextContainer');
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
    const answers = testInfo['randomize_answers'] ? shuffleArray(testInfo.answers) : testInfo.answers;
    for (var answer of answers) {
        let answerDiv = document.createElement('div');
        Object.assign(answerDiv, { name: answer, className: 'draggable', draggable: true });
        let answerDivText = document.createElement('p');
        answerDivText.textContent = answer;
        answerDiv.appendChild(answerDivText);
        answersContainer.appendChild(answerDiv);
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
    const iconObject = document.createElement('img');
    iconObject.style = 'margin-right: 7px;';
    const button = document.getElementById('shaking-button');
    const answersDivs = document.querySelectorAll('div#target');
    const isAnswerDivsFull = Array.from(answersDivs).map(element => !!element.children.length);

    if (!isAnswerDivsFull.includes(true)) {
        button.classList.add('shake');
    } else {
        button.disabled = true;

        const testInfo = await fetch('http://127.0.0.1:8000/db/get/round_info').then(response => response.json());
        const bottomDiv = document.getElementById('bottomDiv');

        // collect my answers into dict['answerText': answerPosition]
        let answersList = {};
        let positionCount = 0;

        answersDivs.forEach(answerDiv => {
            positionCount += 1;
            const gotAnswerText = answerDiv.children[0].name;
            answersList[gotAnswerText] = positionCount;
        });

        // send answers
        let checkingResults = await fetch(
            'http://127.0.0.1:8000/db/send_answers',
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify( {answers: answersList} ),
            }
        ).then(response => response.json());

        const isAllRight = !Object.values(checkingResults).includes(false);
        const audio = new Audio(isAllRight ? '/sounds/right.mp3' : '/sounds/wrong.mp3');
        iconObject.src = isAllRight ? '/images/right.svg' : '/images/wrong.svg';
        audio.volume = 0.4;

        // prepare the bottomDiv
        // title
        const bottomDivTitle = document.createElement('div');
        const bottomDivTitleText = document.createElement('h3');
        bottomDivTitle.classList.add('bottom-div-titlebox');
        bottomDivTitle.appendChild(iconObject);
        bottomDivTitle.appendChild(bottomDivTitleText);
        bottomDiv.appendChild(bottomDivTitle);
        bottomDivTitleText.textContent = isAllRight ? 'Awesome!' : 'Incorrect';
        bottomDiv.classList.add(isAllRight ? 'green-border' : 'red-border');

        // make a text with correct answers
        const parts = testInfo['round_text'].split('/');
        const textTag = document.createElement('pa');

        // sort right answers by position
        var items = Object.keys(checkingResults).map((key) => [key, checkingResults[key]]);
        items.sort((first, second) => first[1] - second[1]);

        // insert right answers into bottomDiv text
        for (var rightData of items) {
            let [rightAnswer, isMyAnswerRight] = rightData;

            // spawn underlined text
            const targetAnswerContainer = document.createElement('b');
            targetAnswerContainer.textContent = rightAnswer;
            targetAnswerContainer.classList.add(isMyAnswerRight ? 'green-underline' : 'red-underline');

            textTag.appendChild(document.createTextNode(parts[0]));
            textTag.appendChild(targetAnswerContainer);
            parts.shift();
        }
        textTag.appendChild(document.createTextNode(parts[0]));
        bottomDiv.appendChild(textTag);

        // "next" button
        const continueButton = document.createElement('button');
        continueButton.textContent = '➤';
        continueButton.classList.add('continue-button');
        continueButton.addEventListener('click', async () => {
            window.location.href = await fetch('http://127.0.0.1:8000/db/next_round').then(response => response.json());
        });
        bottomDiv.appendChild(continueButton);
        bottomDiv.classList.remove('hidden');

        // if i remove hidden class and set the style at the same time, the transition won't work | 0.1s delay is not noticeable
        setTimeout(() => {
            audio.play();
            bottomDiv.style = 'transition: ease-out 0.5s; transform: translateY(-120px);';
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await updateTestInfo();
    setDraggables();

    const button = document.getElementById('shaking-button');
    button.addEventListener('animationend', () => { button.classList.remove('shake'); });
});
