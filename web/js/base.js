// document.addEventListener('DOMContentLoaded', function() {
//     // trying to restrict opening devtools & breaking the logics of test loading & checking

//     document.addEventListener('contextmenu', e => { e.preventDefault(); });
//     document.addEventListener('keydown', e => { e.preventDefault(); });
// });

// a simple def against those who know what base64 is, but don't dare to get into the code 🤗
async function getTestData() {
    let crypted = await eel.get_test_data()();
    crypted = await eel.rot1_decrypt(crypted)();

    return JSON.parse(atob(crypted));
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}
