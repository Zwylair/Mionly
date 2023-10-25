async function updateTestInfo() {
    const testInfo = await eel.get_test_data()();

    const testTitle = document.getElementById("test_title");
    const textContainer = document.getElementById("testTextContainer");
    const answersContainer = document.getElementById("answers_container");

    // spawn the target containers
    const parts = testInfo["test_text"].split('/');
    for (var i = 0; i < parts.length / 2; i += 2) {
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
            // let [isTrue, position] = answerObject[key];
        }

        // make a container for answer radio button and label
        let answerDiv = document.createElement('div');
        answerDiv.name = answerText;
        answerDiv.classList = ['draggable'];
        answerDiv.draggable = 'true';

        let answerDivText = document.createElement('p');
        answerDivText.textContent = answerText;

        answerDiv.appendChild(answerDivText);
        answersContainer.appendChild(answerDiv);
    }

    // update text and desc of test
    testTitle.textContent = testInfo['name'];
}

function setDraggables() {
    const draggables = document.querySelectorAll('.draggable');
    const container = document.querySelector('.container-box');
    const target = document.getElementById('target');
    let draggableWidths = [];

    draggables.forEach(draggable => {
        draggableWidths.push(draggable.offsetWidth);
        draggable.addEventListener('dragstart', () => {
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
        });
    });

    target.style.minWidth = `${Math.max(...draggableWidths) + 15}px`;

    container.addEventListener('dragover', e => {
        e.preventDefault();
    });

    container.addEventListener('drop', e => {
        const draggable = document.querySelector('.dragging');
        container.appendChild(draggable);
        draggable.classList.remove('dragging');
    });

    target.addEventListener('dragover', e => {
        e.preventDefault();

        // Change cursor style to indicate restriction when the target is full
        if (target.children.length > 0) {
            e.dataTransfer.dropEffect = 'none';
        }
    });

    target.addEventListener('dragenter', () => {
        // Change cursor style to indicate restriction when dragging over the target
        if (target.children.length > 0) {
            target.style.cursor = 'not-allowed';
        }
    });

    target.addEventListener('dragleave', () => {
        // Restore the cursor style when leaving the target
        target.style.cursor = 'auto';
    });

    target.addEventListener('drop', e => {
        if (target.children.length === 0) {
            const draggable = document.querySelector('.dragging');
            target.appendChild(draggable);
            draggable.classList.remove('dragging');
        }
    });
}

async function sendSubmit() {
    let answersDivs = document.querySelectorAll('div#target');

    let isAnswerDivsFull = [];
    answersDivs.forEach(element => {
        isAnswerDivsFull.push(!!element.children.length);
    });

    if (!isAnswerDivsFull.includes(true)) {
        alert('You arent picked answer');
    } else {
        const testInfo = await eel.get_test_data()();
        const answers = testInfo['answers'];
        let answersList = [];

        let i = 1;
        answersDivs.forEach(element => {
            let gotAnswerText = element.children[0].name;
            answers.forEach(answerElement => {
                if (Object.keys(answerElement)[0] == gotAnswerText) {
                    answersList.push(answerElement);
                }
            })
            i++;
        });

        await eel.submit_action(answersList)();
        window.location.href = await eel.load_next_test()();
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    await updateTestInfo();
    setDraggables();
});
