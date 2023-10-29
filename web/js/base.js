document.addEventListener('DOMContentLoaded', function() {
    // trying to restrict opening devtools & breaking the logics of test loading when switching between the pages

    document.addEventListener('contextmenu', e => { e.preventDefault(); });
    document.addEventListener('keydown', e => {  if (e.key !== 'F5') { e.preventDefault(); }  });
});

// a small simple defence against those who know what base64 is, but don't dare to get into the code 🤗
async function getTestData() {
    let crypted = await eel.get_test_data()();
    crypted = await eel.rot1_decrypt(crypted)();

    return JSON.parse(atob(crypted));
}
