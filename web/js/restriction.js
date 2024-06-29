document.addEventListener('DOMContentLoaded', function() {
    // trying to restrict opening devtools & breaking the logics of test loading & checking

    // prevent opening the context menu
    document.addEventListener('contextmenu', e => { e.preventDefault(); });

    // allow single key presses (letters, numbers, symbols), block any other key combinations
    document.addEventListener('keydown', function(e) {
        if (e.key && !(e.ctrlKey || e.altKey || e.shiftKey || e.metaKey || e.key.startsWith("F"))) {} else { e.preventDefault(); }
    });
});
