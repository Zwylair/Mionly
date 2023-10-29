async function updateTestInfo() {
    const testInfo = await getTestData();
    const testCounter = document.getElementById('test_counter');
    const testTitle = document.getElementById('test_title');
    const textContainer = document.getElementById('testTextContainer');
    const answersContainer = document.getElementById('answers_container');

    // spawn the target containers
    const parts = testInfo['test_text'].split('/');
    for (var i = 0; i < parts.length / 2; i += 2) {
        // insert a <div> where you want to drag and drop the answer without breaking the <pa>
        const textTag = document.createElement('pa');
        const targetAnswerContainer = document.createElement('div');
        targetAnswerContainer.id = 'target';

        textTag.appendChild(document.createTextNode(parts[i]));
        textTag.appendChild(targetAnswerContainer);
        textTag.appendChild(document.createTextNode(parts[i + 1]));
        
        textContainer.appendChild(textTag);
    }

    // spawn the answers
    for (var answerObject of testInfo['answers']) {
        for (var key in answerObject) {
            answerText = key;
        }

        // make a container for answer radio button and label
        let answerDiv = document.createElement('div');
        Object.assign(answerDiv, { name: answerText, className: 'draggable', draggable: true });

        let answerDivText = document.createElement('p');
        answerDivText.textContent = answerText;

        answerDiv.appendChild(answerDivText);
        answersContainer.appendChild(answerDiv);
    }

    testTitle.textContent = testInfo['name'];
    testCounter.textContent = `${await eel.get_completed_tests_count()() + 1}/${await eel.get_all_tests_count()()}`;
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
    const answersDivs = document.querySelectorAll('div#target');
    const isAnswerDivsFull = Array.from(answersDivs).map(element => !!element.children.length);

    if (!isAnswerDivsFull.includes(true)) {
        // shaking the submit button when there is no picked answer
        const button = document.getElementById('shaking-button');

        button.classList.add('shake');
    } else {
        const answers = (await getTestData()).answers;

        // get the original data with got key
        const answersList = Array.from(answersDivs).map(element => {
            const gotAnswerText = element.children[0].name;
            return answers.find(answerElement => Object.keys(answerElement)[0] === gotAnswerText);
        });

        await eel.submit_action(answersList)();
        window.location.href = await eel.load_next_test()();
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
