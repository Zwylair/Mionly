/**
 * @param {string} ww_book
 * @param {string} unit
 */
async function loadTests(ww_book, unit) {
    const availableTests = await eel.load_tests_list(ww_book, unit)();
    const testsDatalist = document.getElementById('testsList');
    const testInput = document.getElementById('chosenTestInput');

    availableTests.forEach(element => {
        testsDatalist.appendChild(new Option(element));
    });

    testInput.addEventListener('input', async function(event) {
        window.location.href = await eel.start_testing(ww_book, unit, event.target.value)();;
    });
}


/**
 * @param {string} ww_book
 */
async function loadUnits(ww_book) {
    const availableUnits = await eel.load_units_list(ww_book)();
    const unitsDatalist = document.getElementById('unitsList');
    const unitInput = document.getElementById('chosenUnitInput');

    availableUnits.forEach(element => {
        unitsDatalist.appendChild(new Option(element));
    });

    unitInput.addEventListener('input', async function(event) {
        await loadTests(ww_book, event.target.value);
    });
}

async function loadBooks() {
    const availableWWBooks = await eel.load_ww_book_list()();
    const booksDatalist = document.getElementById('booksList');
    const booksInput = document.getElementById('chosenBookInput');

    availableWWBooks.forEach(element => {
        booksDatalist.appendChild(new Option(element));
    });

    booksInput.addEventListener('input', async function(event) {
        await loadUnits(event.target.value);
    });

}

async function quickStart() {
    window.location.href = await eel.start_testing('Wider World 0', 'Unit 0', 'Test 1')();
}

document.addEventListener('DOMContentLoaded', function() {
    loadBooks();
});
