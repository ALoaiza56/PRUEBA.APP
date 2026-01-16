document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links li');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');

    function activateTab(tabId) {
        // Remove active class from all links and contents
        navLinks.forEach(l => l.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        // Find and activate the link
        const targetLink = document.querySelector(`.nav-links li[data-tab="${tabId}"]`);
        if (targetLink) {
            targetLink.classList.add('active');
            // Update page title
            const tabName = targetLink.querySelector('a').textContent;
            if (pageTitle) pageTitle.textContent = tabName;
        }

        // Find and activate the content
        const targetContent = document.getElementById(tabId);
        if (targetContent) {
            targetContent.classList.add('active');
        }
    }

    // Check for hash in URL on load
    const hash = window.location.hash;
    if (hash) {
        activateTab(hash.substring(1));
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const tabId = link.getAttribute('data-tab');
            if (tabId) {
                e.preventDefault();
                history.replaceState(null, null, `#${tabId}`);
                activateTab(tabId);
            }
        });
    });
});
