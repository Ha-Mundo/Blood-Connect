// Enable Bootstrap tooltips 

// Initialize all tooltips on the page
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el))

// Flash messages timeout
setTimeout(function() {
    let alerts = document.querySelectorAll('#flash-container .alert');
    alerts.forEach(function(alert) {
        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000); // 5000ms = 5 sec

/* Function to toggle status view to confirm view for find_blood & donate page */
function toggleConfirm(show){
    document.getElementById('status-view').style.display =
        show ? 'none' : 'block';

    document.getElementById('confirm-view').style.display =
        show ? 'block' : 'none';
}
/**
 * Scroll Persistence Utility
 * Saves the vertical scroll position before form submissions 
 * and restores it after the page reloads.
 */
document.addEventListener("DOMContentLoaded", function() {
    // 1. Capture scroll position on any form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });

    // 2. Restore scroll position if found in session storage
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        // Use a slight timeout to ensure content is rendered before scrolling
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('scrollPosition');
    }
});