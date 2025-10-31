/**
 * CodeGate Web Interface - Main JavaScript
 * Handles real-time updates, UI interactions, and API communication
 */

// Global variables
let currentUser = null;
let notifications = [];

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Setup navigation
    setupNavigation();
    
    // Setup real-time updates
    setupRealTimeUpdates();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    console.log('CodeGate Web Interface initialized');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap modals
 */
function initializeModals() {
    // Auto-focus on modal inputs when opened
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const autofocusElement = modal.querySelector('[autofocus]');
            if (autofocusElement) {
                autofocusElement.focus();
            }
        });
    });
}

/**
 * Setup navigation highlights and interactions
 */
function setupNavigation() {
    // Highlight current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath.startsWith(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Setup real-time updates using WebSocket
 */
function setupRealTimeUpdates() {
    if (typeof io !== 'undefined') {
        // Socket.IO is available, setup real-time features
        window.socket = io();
        
        window.socket.on('connect', function() {
            console.log('Connected to CodeGate real-time server');
            showNotification('Connected to real-time updates', 'success');
        });
        
        window.socket.on('disconnect', function() {
            console.log('Disconnected from real-time server');
            showNotification('Real-time connection lost', 'warning');
        });
        
        window.socket.on('system_notification', function(data) {
            showNotification(data.message, data.type || 'info');
        });
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N: New scan
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            window.location.href = '/scan';
        }
        
        // Ctrl/Cmd + H: History
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            window.location.href = '/history';
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) modal.hide();
            }
        }
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = {
        id: Date.now(),
        message: message,
        type: type,
        timestamp: new Date()
    };
    
    notifications.push(notification);
    
    // Create toast element
    const toast = createToastElement(notification);
    
    // Add to toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration
    });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
        notifications = notifications.filter(n => n.id !== notification.id);
    });
}

/**
 * Create toast element
 */
function createToastElement(notification) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    
    const iconMap = {
        success: 'bi-check-circle',
        error: 'bi-exclamation-triangle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };
    
    const colorMap = {
        success: 'text-success',
        error: 'text-danger',
        warning: 'text-warning',
        info: 'text-primary'
    };
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="bi ${iconMap[notification.type]} ${colorMap[notification.type]} me-2"></i>
            <strong class="me-auto">CodeGate</strong>
            <small class="text-muted">${formatTime(notification.timestamp)}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${notification.message}
        </div>
    `;
    
    return toast;
}

/**
 * Format time for display
 */
function formatTime(date) {
    return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Utility function to format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function to format duration
 */
function formatDuration(seconds) {
    if (seconds < 1) {
        return (seconds * 1000).toFixed(0) + 'ms';
    } else if (seconds < 60) {
        return seconds.toFixed(1) + 's';
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }
}

/**
 * Utility function to get risk level from score
 */
function getRiskLevel(score) {
    if (score < 25) return 'low';
    if (score < 50) return 'medium';
    if (score < 75) return 'high';
    return 'critical';
}

/**
 * Utility function to get risk color from score
 */
function getRiskColor(score) {
    if (score < 25) return 'success';
    if (score < 50) return 'warning';
    if (score < 75) return 'danger';
    return 'dark';
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success', 2000);
        }).catch(() => {
            showNotification('Failed to copy to clipboard', 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard', 'success', 2000);
        } catch (err) {
            showNotification('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Animate counting up to a number
 */
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    requestAnimationFrame(animate);
}

/**
 * Create a loading spinner element
 */
function createLoadingSpinner(size = 'sm') {
    const spinner = document.createElement('div');
    spinner.className = `spinner-border spinner-border-${size}`;
    spinner.setAttribute('role', 'status');
    
    const srText = document.createElement('span');
    srText.className = 'visually-hidden';
    srText.textContent = 'Loading...';
    spinner.appendChild(srText);
    
    return spinner;
}

/**
 * Show loading state on button
 */
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = createLoadingSpinner().outerHTML + ' Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

/**
 * API request wrapper with error handling
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('API request failed:', error);
        showNotification(`Request failed: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

/**
 * Download file from URL
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Validate Python code syntax (basic)
 */
function validatePythonCode(code) {
    const errors = [];
    const lines = code.split('\n');
    
    // Basic syntax checks
    let indentLevel = 0;
    let inString = false;
    let stringChar = '';
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lineNum = i + 1;
        
        // Check for basic syntax issues
        if (line.trim()) {
            // Check indentation consistency
            const leadingSpaces = line.match(/^ */)[0].length;
            if (leadingSpaces % 4 !== 0 && leadingSpaces > 0) {
                errors.push(`Line ${lineNum}: Inconsistent indentation`);
            }
        }
        
        // Check for unmatched parentheses, brackets, braces
        let parenCount = 0;
        let bracketCount = 0;
        let braceCount = 0;
        
        for (let char of line) {
            if (!inString) {
                if (char === '(' || char === '[' || char === '{') {
                    if (char === '(') parenCount++;
                    else if (char === '[') bracketCount++;
                    else if (char === '{') braceCount++;
                } else if (char === ')' || char === ']' || char === '}') {
                    if (char === ')') parenCount--;
                    else if (char === ']') bracketCount--;
                    else if (char === '}') braceCount--;
                }
                
                if (char === '"' || char === "'") {
                    inString = true;
                    stringChar = char;
                }
            } else if (char === stringChar) {
                inString = false;
                stringChar = '';
            }
        }
        
        if (parenCount !== 0 || bracketCount !== 0 || braceCount !== 0) {
            errors.push(`Line ${lineNum}: Unmatched brackets or parentheses`);
        }
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Auto-resize textareas on input
document.addEventListener('input', function(e) {
    if (e.target.tagName === 'TEXTAREA' && e.target.classList.contains('auto-resize')) {
        autoResizeTextarea(e.target);
    }
});

// Export utilities for use in other scripts
window.CodeGateUtils = {
    showNotification,
    copyToClipboard,
    formatFileSize,
    formatDuration,
    getRiskLevel,
    getRiskColor,
    debounce,
    animateCounter,
    setButtonLoading,
    apiRequest,
    downloadFile,
    validatePythonCode,
    autoResizeTextarea
};
