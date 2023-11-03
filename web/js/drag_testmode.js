async function updateTestInfo() {
    const testInfo = await getTestData();
    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById('test_title');
    const textContainer = document.getElementById('testTextContainer');
    const answersContainer = document.getElementById('answers_container');

    // spawn the target containers
    const parts = testInfo['test_text'].split('/');
    const textTag = document.createElement('pa');

    for (var i = 0; i < parts.slice(0, -1).length; i += 1) {
        // insert a <div> where you want to drag and drop the answer without breaking the <pa>
        const targetAnswerContainer = document.createElement('div');
        targetAnswerContainer.id = 'target';

        textTag.appendChild(document.createTextNode(parts[i]));
        textTag.appendChild(targetAnswerContainer);
    }
    textTag.appendChild(document.createTextNode(parts[parts.length - 1]));
    textContainer.appendChild(textTag);

    // spawn the answers
    const answers = shuffleArray(Object.keys(testInfo.answers));
    for (var key of answers) {
        answerText = key;

        // make a container for answer radio button and label
        let answerDiv = document.createElement('div');
        Object.assign(answerDiv, { name: answerText, className: 'draggable', draggable: true });

        let answerDivText = document.createElement('p');
        answerDivText.textContent = answerText;

        answerDiv.appendChild(answerDivText);
        answersContainer.appendChild(answerDiv);
    }

    testTitle.textContent = testInfo['name'];
    testCounter.textContent = `${await eel.get_all_tests_count()() - await eel.get_available_tests_count()()}/${await eel.get_all_tests_count()()}`;
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
    const rightIcon = document.createElement('span');
    rightIcon.classList.add('material-symbols-outlined');
    rightIcon.textContent = 'task_alt';

    const wrongIcon = document.createElement('span');
    wrongIcon.classList.add('material-symbols-outlined');
    wrongIcon.textContent = 'dangerous';

    //

    const answersDivs = document.querySelectorAll('div#target');
    const isAnswerDivsFull = Array.from(answersDivs).map(element => !!element.children.length);
    const button = document.getElementById('shaking-button');

    if (!isAnswerDivsFull.includes(true)) {
        // shaking the submit button when there is no picked answer
        button.classList.add('shake');
    } else {
        button.setAttribute('disabled', 'disabled');

        const testInfo = await getTestData();
        const bottomDiv = document.getElementById('bottomDiv');

        // get the original data with got key
        let answersList = {};
        answersDivs.forEach(answerDiv => {
            const gotAnswerText = answerDiv.children[0].name;
            answersList[gotAnswerText] = testInfo.answers[gotAnswerText];
        })

        // dump the progress
        const hasError = await eel.submit_action(answersList)();

        const audio = new Audio(`sounds/${hasError ? 'wrong' : 'right'}.mp3`);
        audio.volume = 0.4;

        // prepare the bottomDiv
        const bottomDivTitle = document.createElement('div');
        const bottomDivTitleText = document.createElement('h3');

        // header template
        bottomDivTitle.classList.add('bottom-div-titlebox');
        bottomDivTitle.appendChild(hasError ? wrongIcon : rightIcon)
        bottomDivTitle.appendChild(bottomDivTitleText);

        // show the bottomDiv
        bottomDiv.classList.remove('hidden');

        if (!hasError) {
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
            const parts = testInfo['test_text'].split('/');
            const textTag = document.createElement('pa');

            // filtering out wrong answers (wrong answers always have position 0)
            let allRightAnswers = {};

            Object.keys(testInfo.answers).forEach( answerText => {
                const info = testInfo.answers[answerText];
                if (info[1] !== 0) {
                    allRightAnswers[answerText] = info;
                }
            })
            const rightAnswersKeys = Object.keys(allRightAnswers);
            const givenAnswersKeys = Object.keys(answersList);

            for (var i = 0; i < parts.slice(0, -1).length; i += 1) {
                // spawn underlined text
                const targetAnswerContainer = document.createElement('b');
                targetAnswerContainer.textContent = rightAnswersKeys[i]
                targetAnswerContainer.classList.add(givenAnswersKeys[i] === rightAnswersKeys[i] ? 'green-underline' : 'red-underline');

                textTag.appendChild(document.createTextNode(parts[i]));
                textTag.appendChild(targetAnswerContainer);
            }
            textTag.appendChild(document.createTextNode(parts[parts.length - 1]));
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

document.addEventListener('DOMContentLoaded', async function () {
    await updateTestInfo();
    setDraggables();

    const button = document.getElementById('shaking-button');

    button.addEventListener('animationend', function () {
        button.classList.remove('shake');
    });
});
