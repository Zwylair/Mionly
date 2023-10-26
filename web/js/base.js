document.addEventListener('DOMContentLoaded', function() {
    // trying to restrict opening devtools & breaking the logics of test loading when switching between the pages
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });
    document.addEventListener('keydown', function (e) {
        if (e.key !== 'F5') {
            e.preventDefault();
        }
    });
});
