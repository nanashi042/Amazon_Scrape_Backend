// Main JavaScript file

// Close modal when pressing Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('trackerModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const urlForm = document.querySelector('.url-input-form');
    if (urlForm) {
        const urlInput = urlForm.querySelector('.url-input');
        
        // Validate URL on input
        urlInput.addEventListener('blur', function() {
            if (this.value) {
                try {
                    new URL(this.value);
                    this.classList.remove('error');
                } catch (e) {
                    this.classList.add('error');
                }
            }
        });
    }

    // Tracker form validation
    const trackerForm = document.querySelector('.tracker-form');
    if (trackerForm) {
        const targetPriceInput = trackerForm.querySelector('input[name="target_price"]');
        
        if (targetPriceInput) {
            targetPriceInput.addEventListener('change', function() {
                const maxPrice = parseFloat(this.max);
                const currentPrice = parseFloat(this.value);
                
                if (currentPrice >= maxPrice) {
                    this.classList.add('error');
                    this.parentElement.querySelector('small').textContent = 
                        `Target price must be less than current price: ${maxPrice}`;
                } else {
                    this.classList.remove('error');
                    this.parentElement.querySelector('small').textContent = 
                        `Must be less than current price: ${this.max}`;
                }
            });
        }
    }
});
