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
 * Asynchronous Form Submission (AJAX)
 * Prevents full page reloads and visual flickering on admin actions.
 */
document.addEventListener("submit", async function(e) {
    // Apply only to forms with the 'ajax-form' class
    const form = e.target.closest('.ajax-form');
    if (!form) return;

    e.preventDefault(); // Prevents the physical page reload

    // Collects form data and the specific clicked submit button
    const submitter = e.submitter;
    const formData = new FormData(form);
    if (submitter && submitter.name) {
        formData.append(submitter.name, submitter.value);
    }

    try {
        // Sends data to Flask in the background
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });

        if (response.ok) {
            // Extracts the new HTML returned by Flask (after redirect)
            const html = await response.text();
            
            // Replaces the body content invisibly
            const newDoc = new DOMParser().parseFromString(html, "text/html");
            document.body.innerHTML = newDoc.body.innerHTML;
        }
    } catch (error) {
        console.error("Error during the action:", error);
    }
});