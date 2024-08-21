const storedTheme = localStorage.getItem('theme');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (storedTheme) {
    document.documentElement.setAttribute('data-theme', storedTheme);
} else {
    document.documentElement.setAttribute('data-theme', prefersDarkScheme ? 'dark' : 'light');
}

function toggleTheme() {
    let currentTheme = localStorage.getItem('theme');
    let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}
