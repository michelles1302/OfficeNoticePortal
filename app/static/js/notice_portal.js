/* Notice Portal JavaScript Helpers */

document.addEventListener('DOMContentLoaded', function() {
    // Handle AJAX Notice Acknowledgement
    const ackForms = document.querySelectorAll('.form-acknowledge-ajax');
    ackForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = form.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(new FormData(form))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btn.className = 'btn btn-sm btn-success disabled';
                    btn.innerHTML = '✓ Read';
                    // Update unread count if element exists
                    const unreadBadge = document.getElementById('stat-unread-count');
                    if (unreadBadge) {
                        let currentCount = parseInt(unreadBadge.textContent) || 0;
                        if (currentCount > 0) {
                            unreadBadge.textContent = currentCount - 1;
                        }
                    }
                    // Remove unread highlight if present
                    const card = form.closest('.notice-card');
                    if (card) {
                        card.classList.remove('unread-highlight');
                    }
                } else {
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                    alert(data.message || 'Failed to update read status.');
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.innerHTML = originalText;
                console.error('Error acknowledging notice:', error);
            });
        });
    });

    // File input preview handler
    const fileInput = document.getElementById('attachments');
    const fileListPreview = document.getElementById('file-list-preview');
    if (fileInput && fileListPreview) {
        fileInput.addEventListener('change', function() {
            fileListPreview.innerHTML = '';
            if (this.files.length > 0) {
                const list = document.createElement('ul');
                list.className = 'list-unstyled mt-2 text-muted small';
                Array.from(this.files).forEach(file => {
                    const item = document.createElement('li');
                    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                    item.innerHTML = `📄 <strong>${file.name}</strong> (${sizeMB} MB)`;
                    list.appendChild(item);
                });
                fileListPreview.appendChild(list);
            }
        });
    }
});
