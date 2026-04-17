/**
 * UI Lifecycle Manager
 * Handles tooltips and Flash-to-Toast auto-dismissal
 */
const UI = {
    init: function() {
        // 1. Initialize Tooltips (using the latest Bootstrap constructor)
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(el => {
            // Clean up old instances to prevent memory leaks before re-init
            const oldInstance = bootstrap.Tooltip.getInstance(el);
            if (oldInstance) oldInstance.dispose();
            new bootstrap.Tooltip(el);
        });

        // 2. Flash messages auto-dismissal (5-second timer)
        setTimeout(() => {
            const alerts = document.querySelectorAll('#flash-container .alert');
            alerts.forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                if (bsAlert) bsAlert.close();
            });
        }, 5000);
    },

    toggleConfirm: function(show) {
        const statusView = document.getElementById('status-view');
        const confirmView = document.getElementById('confirm-view');
        if (statusView && confirmView) {
            statusView.style.display = show ? 'none' : 'block';
            confirmView.style.display = show ? 'block' : 'none';
        }
    }
};

// Initial Load
document.addEventListener("DOMContentLoaded", UI.init);

/**
 * Global AJAX Form Handler
 * Targeted at forms with 'ajax-form' class to prevent page flickering.
 */
document.addEventListener("submit", async function(e) {
    const form = e.target.closest('.ajax-form');
    if (!form) return;

    e.preventDefault();

    const submitter = e.submitter;
    const formData = new FormData(form);
    if (submitter && submitter.name) {
        formData.append(submitter.name, submitter.value);
    }

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });

        if (response.ok) {
            const html = await response.text();
            const newDoc = new DOMParser().parseFromString(html, "text/html");
            
            // Perform the swap
            document.body.innerHTML = newDoc.body.innerHTML;
            
            // Re-run UI initializers for the new DOM elements
            UI.init();
        }
    } catch (error) {
        console.error("AJAX Action Failed:", error);
    }
});