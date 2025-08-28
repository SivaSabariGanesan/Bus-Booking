document.addEventListener('DOMContentLoaded', function() {
    // Check if theme toggle already exists to prevent duplicates
    if (document.querySelector('.theme-toggle')) {
        return;
    }

    // Theme toggle functionality
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = '🌙';
    themeToggle.title = 'Toggle Theme';
    themeToggle.setAttribute('aria-label', 'Toggle dark/light theme');
    
    // Get current theme from localStorage or default to light
    let currentTheme = localStorage.getItem('admin-theme') || 'light';
    
    // Apply theme immediately
    applyTheme(currentTheme);
    updateToggleIcon(currentTheme);
    
    // Add toggle button to page
    document.body.appendChild(themeToggle);
    
    // Toggle theme on click
    themeToggle.addEventListener('click', function() {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(currentTheme);
        localStorage.setItem('admin-theme', currentTheme);
        updateToggleIcon(currentTheme);
    });
    
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        // Also set a class on body for additional styling
        document.body.classList.toggle('dark-theme', theme === 'dark');
    }
    
    function updateToggleIcon(theme) {
        themeToggle.innerHTML = theme === 'light' ? '🌙' : '☀️';
        themeToggle.title = theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
        themeToggle.setAttribute('aria-label', theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode');
    }
});
