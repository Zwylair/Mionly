async function uploadFile() {
    const formData = new FormData();
    const fileInput = document.getElementById('file_input');
    formData.append('file', fileInput.files[0]);

    const response = await fetch('db/upload_file', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    console.log(result);
}
 
async function fetchJson(url) {
    const response = await fetch(url);
    return response.json();
}

async function loadTests() {
    const availableTests = await fetchJson('http://127.0.0.1:8000/db/get/available_tests');
    const testsDatalist = document.getElementById('test_list');
    const testInput = document.getElementById('chosen_test');

    availableTests.forEach(element => {
        testsDatalist.appendChild(new Option(element));
    });

    testInput.addEventListener('input', async (event) => {
        const randomizeRounds = document.getElementById('randomize_rounds_checkbox').checked;
        const randomizeAnswers = document.getElementById('randomize_answers_checkbox').checked;

        window.location.href = await fetch(
            'http://127.0.0.1:8000/db/start_test',
            {
                method: "POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: event.target.value,
                    randomize_rounds: randomizeRounds,
                    randomize_answers: randomizeAnswers
                }),
            }
        ).then(response => response.json());
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetch('http://127.0.0.1:8000/db/wipe');
    loadTests();
});
