async function uploadAndStart() {
    const formData = new FormData();
    const fileInput = document.getElementById('file_input');
    formData.append('file', fileInput.files[0]);

    const response = await fetch('db/upload_file', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    await startTest(result['file_path']);
}

async function fetchJson(url) {
    const response = await fetch(url);
    return response.json();
}

async function startTest(testname) {
    const randomizeRounds = document.getElementById('randomize_rounds_checkbox').checked;
    const randomizeAnswers = document.getElementById('randomize_answers_checkbox').checked;

    window.location.href = await fetch(
        'db/start_test',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: testname,
                randomize_rounds: randomizeRounds,
                randomize_answers: randomizeAnswers
            }),
        }
    ).then(response => response.json());
}

async function loadTests() {
    const availableTests = await fetchJson('db/get/available_tests');
    const testsDatalist = document.getElementById('test_list');
    const testInput = document.getElementById('chosen_test');

    availableTests.forEach(element => {
        testsDatalist.appendChild(new Option(element));
    });

    testInput.addEventListener('input', async (event) => { await startTest(event.target.value) });
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetch('db/wipe');
    loadTests();
});
