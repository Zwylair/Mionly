/**
 * @param {string} ww_book
 * @param {string} unit
 */
async function loadTests(ww_book, unit) {
    let availableTests = await eel.load_tests_list(ww_book, unit)();
    const testsDatalist = document.getElementById("testsList");
    const testInput = document.getElementById("chosenTestInput");

    availableTests.forEach(element => {
        let option = document.createElement('option');
        option.value = element;

        testsDatalist.appendChild(option);
    });

    testInput.addEventListener("input", async function(event) {
        const inputValue = event.target.value;

        let firstTestUrl = await eel.start_testing(ww_book, unit, inputValue)();
        window.location.href = firstTestUrl;
    });
}


/**
 * @param {string} ww_book
 */
async function loadUnits(ww_book) {
    let availableUnits = await eel.load_units_list(ww_book)();
    const unitsDatalist = document.getElementById("unitsList");
    const unitInput = document.getElementById("chosenUnitInput");

    availableUnits.forEach(element => {
        let option = document.createElement('option');
        option.value = element;

        unitsDatalist.appendChild(option);
    });

    unitInput.addEventListener("input", async function(event) {
        const inputValue = event.target.value;
        
        await loadTests(ww_book, inputValue);
    });
}

async function loadBooks() {
    let availableWWBooks = await eel.load_ww_book_list()();
    const booksDatalist = document.getElementById("booksList");
    const booksInput = document.getElementById("chosenBookInput");

    availableWWBooks.forEach(element => {
        let option = document.createElement('option');
        option.value = element;

        booksDatalist.appendChild(option);
    });

    booksInput.addEventListener("input", async function(event) {
        const inputValue = event.target.value;
        await loadUnits(inputValue);
    });

}

async function quickStart() {
    let firstTestUrl = await eel.start_testing('Wider World 0', 'Unit 0', 'Test 1')();
    window.location.href = firstTestUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    loadBooks()
});
