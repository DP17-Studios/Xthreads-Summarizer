// ===========================
// MODERN THREADCRAFT FUNCTIONALITY
// ===========================

// App state management
const AppState = {
    isLoading: false,
    currentStep: 0,
    processingTexts: [
        'Analyzing content...',
        'Extracting key insights...',
        'Processing thread structure...',
        'Identifying main themes...',
        'Generating summary points...',
        'Finalizing results...'
    ],
    currentProcessingIndex: 0
};

// DOM Elements Cache
const Elements = {
    form: null,
    urlInput: null,
    submitButton: null,
    loading: null,
    validator: null,
    typingText: null,
    init() {
        this.form = document.getElementById('thread-form');
        this.urlInput = document.getElementById('url');
        this.submitButton = document.getElementById('submit-btn');
        this.loading = document.getElementById('loading');
        this.validator = document.querySelector('.url-validator');
        this.typingText = document.getElementById('typing-text');
    }
};

// ===========================
// INITIALIZATION
// ===========================

document.addEventListener('DOMContentLoaded', function() {
    Elements.init();
    initializeAnimations();
    initializeFormHandlers();
    initializeUrlValidation();
    initializeExampleButtons();
    initializeResultsInteractions();
    initializeKeyboardShortcuts();
    
    // Auto-focus on URL input with a slight delay for better UX
    setTimeout(() => {
        if (Elements.urlInput) {
            Elements.urlInput.focus();
        }
    }, 500);
});

// ===========================
// ANIMATION SYSTEM
// ===========================

function initializeAnimations() {
    // Trigger entrance animations for cards
    const cards = document.querySelectorAll('.card-animation');
    cards.forEach((card, index) => {
        const delay = card.dataset.delay || 0;
        setTimeout(() => {
            card.style.animationPlayState = 'running';
        }, parseInt(delay));
    });
    
    // Initialize scroll-triggered animations
    initializeScrollAnimations();
    
    // Add mouse movement parallax effect to floating shapes
    initializeParallaxEffect();
}

function initializeScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }
    );
    
    // Observe bullet points for staggered animation
    const bulletPoints = document.querySelectorAll('.bullet-point');
    bulletPoints.forEach(point => observer.observe(point));
}

function initializeParallaxEffect() {
    if (window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
        document.addEventListener('mousemove', (e) => {
            const shapes = document.querySelectorAll('.shape');
            const mouseX = e.clientX / window.innerWidth;
            const mouseY = e.clientY / window.innerHeight;
            
            shapes.forEach((shape, index) => {
                const speed = (index + 1) * 0.02;
                const x = (mouseX - 0.5) * speed * 100;
                const y = (mouseY - 0.5) * speed * 100;
                
                shape.style.transform = `translate(${x}px, ${y}px)`;
            });
        });
    }
}

// ===========================
// FORM HANDLING
// ===========================

function initializeFormHandlers() {
    if (!Elements.form) return;
    
    Elements.form.addEventListener('submit', handleFormSubmit);
    
    // Enhanced button interactions
    if (Elements.submitButton) {
        Elements.submitButton.addEventListener('mouseenter', createRippleEffect);
        Elements.submitButton.addEventListener('click', createClickRipple);
    }
}

function handleFormSubmit(e) {
    if (!isValidUrl(Elements.urlInput.value)) {
        e.preventDefault();
        showUrlError('Please enter a valid Twitter/X thread URL');
        return;
    }
    
    setLoadingState(true);
    startProcessingAnimation();
}

function createRippleEffect(e) {
    const ripple = e.target.querySelector('.btn-ripple');
    if (ripple) {
        ripple.style.left = `${e.offsetX - 150}px`;
        ripple.style.top = `${e.offsetY - 150}px`;
    }
}

function createClickRipple(e) {
    if (e.target.disabled) return;
    
    const ripple = e.target.querySelector('.btn-ripple');
    if (ripple) {
        ripple.style.width = '300px';
        ripple.style.height = '300px';
        
        setTimeout(() => {
            ripple.style.width = '0';
            ripple.style.height = '0';
        }, 300);
    }
}

// ===========================
// URL VALIDATION
// ===========================

function initializeUrlValidation() {
    if (!Elements.urlInput) return;
    
    let validationTimeout;
    
    Elements.urlInput.addEventListener('input', (e) => {
        clearTimeout(validationTimeout);
        
        validationTimeout = setTimeout(() => {
            validateUrlInput(e.target.value);
        }, 300);
    });
    
    Elements.urlInput.addEventListener('paste', (e) => {
        setTimeout(() => {
            validateUrlInput(e.target.value);
        }, 10);
    });
}

function validateUrlInput(url) {
    const trimmedUrl = url.trim();
    
    if (!trimmedUrl) {
        hideUrlValidator();
        resetInputState();
        return;
    }
    
    if (isValidUrl(trimmedUrl)) {
        showUrlValidator(true);
        setInputState('valid');
    } else {
        hideUrlValidator();
        setInputState('invalid');
    }
}

function isValidUrl(url) {
    const urlPattern = /^https?:\/\/(www\.)?(twitter|x)\.com\/\w+\/status\/\d+/;
    return urlPattern.test(url);
}

function showUrlValidator(isValid = true) {
    if (!Elements.validator) return;
    
    const icon = Elements.validator.querySelector('.validator-icon i');
    const text = Elements.validator.querySelector('.validator-text');
    
    if (isValid) {
        icon.className = 'fas fa-check-circle';
        text.textContent = 'Valid Twitter/X URL detected';
        Elements.validator.style.background = 'rgba(34, 197, 94, 0.1)';
        Elements.validator.style.borderColor = 'rgba(34, 197, 94, 0.2)';
        Elements.validator.style.color = 'var(--success-600)';
    }
    
    Elements.validator.classList.add('show');
}

function hideUrlValidator() {
    if (Elements.validator) {
        Elements.validator.classList.remove('show');
    }
}

function setInputState(state) {
    if (!Elements.urlInput) return;
    
    Elements.urlInput.classList.remove('valid', 'invalid');
    
    if (state !== 'default') {
        Elements.urlInput.classList.add(state);
    }
}

function resetInputState() {
    setInputState('default');
}

function showUrlError(message) {
    // Create or update error message
    let errorElement = document.querySelector('.url-error');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'url-error';
        errorElement.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span class="error-text">${message}</span>
        `;
        
        Elements.urlInput.parentNode.appendChild(errorElement);
    } else {
        errorElement.querySelector('.error-text').textContent = message;
    }
    
    errorElement.style.display = 'flex';
    setInputState('invalid');
    
    // Auto-hide error after delay
    setTimeout(() => {
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }, 5000);
}

// ===========================
// LOADING STATES
// ===========================

function setLoadingState(loading) {
    AppState.isLoading = loading;
    
    if (Elements.submitButton) {
        Elements.submitButton.disabled = loading;
        
        if (loading) {
            Elements.submitButton.innerHTML = `
                <div class="btn-content">
                    <div class="btn-icon">
                        <i class="fas fa-spinner fa-spin"></i>
                    </div>
                    <span class="btn-text">Processing...</span>
                    <div class="btn-ripple"></div>
                </div>
                <div class="btn-glow"></div>
            `;
        } else {
            Elements.submitButton.innerHTML = `
                <div class="btn-content">
                    <div class="btn-icon">
                        <i class="fas fa-magic"></i>
                    </div>
                    <span class="btn-text">Summarize</span>
                    <div class="btn-ripple"></div>
                </div>
                <div class="btn-glow"></div>
            `;
        }
    }
    
    if (Elements.loading) {
        Elements.loading.style.display = loading ? 'block' : 'none';
    }
}

function startProcessingAnimation() {
    if (!Elements.loading) return;
    
    AppState.currentStep = 0;
    AppState.currentProcessingIndex = 0;
    
    // Start typing animation
    startTypingAnimation();
    
    // Start pipeline animation
    setTimeout(() => {
        animateProcessingPipeline();
    }, 1000);
}

function startTypingAnimation() {
    if (!Elements.typingText) return;
    
    const typeText = (text, callback) => {
        Elements.typingText.textContent = '';
        let index = 0;
        
        const typeInterval = setInterval(() => {
            if (index < text.length) {
                Elements.typingText.textContent += text[index];
                index++;
            } else {
                clearInterval(typeInterval);
                if (callback) callback();
            }
        }, 50);
    };
    
    const cycleTexts = () => {
        const currentText = AppState.processingTexts[AppState.currentProcessingIndex];
        
        typeText(currentText, () => {
            setTimeout(() => {
                AppState.currentProcessingIndex = 
                    (AppState.currentProcessingIndex + 1) % AppState.processingTexts.length;
                cycleTexts();
            }, 1500);
        });
    };
    
    cycleTexts();
}

function animateProcessingPipeline() {
    const steps = document.querySelectorAll('.pipeline-step');
    
    if (steps.length === 0) return;
    
    const animateStep = (index) => {
        if (index >= steps.length) {
            // Restart animation
            setTimeout(() => {
                steps.forEach(step => step.classList.remove('active'));
                setTimeout(() => animateStep(0), 500);
            }, 2000);
            return;
        }
        
        steps[index].classList.add('active');
        
        setTimeout(() => {
            animateStep(index + 1);
        }, 1500);
    };
    
    animateStep(0);
}

// ===========================
// EXAMPLE BUTTONS
// ===========================

function initializeExampleButtons() {
    const exampleButtons = document.querySelectorAll('.example-url');
    
    exampleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const url = button.getAttribute('onclick').match(/'([^']+)'/)[1];
            fillExample(url);
        });
    });
}

function fillExample(url) {
    if (Elements.urlInput) {
        Elements.urlInput.value = url;
        validateUrlInput(url);
        
        // Add a nice fill animation
        Elements.urlInput.style.transform = 'scale(1.02)';
        setTimeout(() => {
            Elements.urlInput.style.transform = 'scale(1)';
        }, 200);
        
        Elements.urlInput.focus();
    }
}

// ===========================
// RESULTS INTERACTIONS
// ===========================

function initializeResultsInteractions() {
    // These functions will be available globally for onclick handlers
    window.copyPoint = copyPoint;
    window.sharePoint = sharePoint;
    window.copyAllPoints = copyAllPoints;
    window.shareResults = shareResults;
    window.downloadSummary = downloadSummary;
    window.resetForm = resetForm;
    window.reportIssue = reportIssue;
}

function copyPoint(index) {
    const bulletPoints = document.querySelectorAll('.bullet-point');
    
    if (bulletPoints[index]) {
        const pointText = bulletPoints[index].querySelector('.point-text').textContent;
        const fullText = `${index + 1}. ${pointText}`;
        
        copyToClipboard(fullText).then(() => {
            showCopyFeedback(bulletPoints[index], 'Point copied!');
        });
    }
}

function sharePoint(index) {
    const bulletPoints = document.querySelectorAll('.bullet-point');
    
    if (bulletPoints[index] && navigator.share) {
        const pointText = bulletPoints[index].querySelector('.point-text').textContent;
        const shareData = {
            title: 'Thread Summary Point',
            text: `${index + 1}. ${pointText}`,
            url: window.location.href
        };
        
        navigator.share(shareData).catch(console.error);
    } else {
        copyPoint(index);
    }
}

function copyAllPoints() {
    const bulletPoints = document.querySelectorAll('.bullet-point');
    const author = document.querySelector('.author-info .value')?.textContent || 'Unknown';
    const tweetCount = document.querySelector('.metadata-item .value')?.textContent || '0';
    
    let summaryText = `Thread Summary by ${author} (${tweetCount} tweets)\n\n`;
    
    bulletPoints.forEach((point, index) => {
        const text = point.querySelector('.point-text').textContent;
        summaryText += `${index + 1}. ${text}\n\n`;
    });
    
    summaryText += `Generated by ThreadCraft - ${window.location.href}`;
    
    copyToClipboard(summaryText).then(() => {
        const copyBtn = document.querySelector('.copy-all-btn');
        showCopyFeedback(copyBtn, 'Summary copied!');
    });
}

function shareResults() {
    const author = document.querySelector('.author-info .value')?.textContent || 'Unknown';
    
    if (navigator.share) {
        const shareData = {
            title: `Thread Summary by ${author}`,
            text: 'Check out this AI-generated thread summary!',
            url: window.location.href
        };
        
        navigator.share(shareData).catch(console.error);
    } else {
        copyToClipboard(window.location.href).then(() => {
            showCopyFeedback(document.querySelector('[onclick="shareResults()"]'), 'Link copied!');
        });
    }
}

function downloadSummary() {
    const bulletPoints = document.querySelectorAll('.bullet-point');
    const author = document.querySelector('.author-info .value')?.textContent || 'Unknown';
    const tweetCount = document.querySelector('.metadata-item .value')?.textContent || '0';
    const originalUrl = document.querySelector('.view-original-btn')?.href || '';
    
    let content = `Thread Summary\n${'='.repeat(50)}\n\n`;
    content += `Author: ${author}\n`;
    content += `Tweet Count: ${tweetCount}\n`;
    content += `Original URL: ${originalUrl}\n`;
    content += `Generated: ${new Date().toLocaleDateString()}\n\n`;
    content += `Summary:\n${'-'.repeat(20)}\n\n`;
    
    bulletPoints.forEach((point, index) => {
        const text = point.querySelector('.point-text').textContent;
        content += `${index + 1}. ${text}\n\n`;
    });
    
    content += `\n${'='.repeat(50)}\n`;
    content += `Generated by ThreadCraft - AI-Powered Thread Summarizer\n`;
    content += `${window.location.origin}\n`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `thread-summary-${author}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess('Summary downloaded successfully!');
}

function resetForm() {
    if (Elements.urlInput) {
        Elements.urlInput.value = '';
        resetInputState();
        hideUrlValidator();
        Elements.urlInput.focus();
    }
    
    setLoadingState(false);
    
    // Hide results and errors with animation
    const elementsToHide = ['.results-section', '.error-section'];
    elementsToHide.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                element.style.display = 'none';
            }, 300);
        }
    });
}

function reportIssue() {
    const errorMessage = document.querySelector('.error-message')?.textContent || 'Unknown error';
    const url = Elements.urlInput?.value || 'No URL provided';
    
    const issueBody = `**Error Report**\n\n` +
        `**URL:** ${url}\n` +
        `**Error:** ${errorMessage}\n` +
        `**Browser:** ${navigator.userAgent}\n` +
        `**Timestamp:** ${new Date().toISOString()}\n\n` +
        `**Additional Details:**\n(Please describe what you were trying to do)`;
    
    const githubUrl = `https://github.com/your-repo/threadcraft/issues/new?` +
        `title=Thread%20Processing%20Error&` +
        `body=${encodeURIComponent(issueBody)}`;
    
    window.open(githubUrl, '_blank');
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            return true;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

function showCopyFeedback(element, message) {
    const originalContent = element.innerHTML;
    const originalBg = element.style.backgroundColor;
    
    element.innerHTML = `<i class="fas fa-check"></i>${message}`;
    element.style.backgroundColor = 'var(--success-500)';
    element.style.transform = 'scale(1.05)';
    
    setTimeout(() => {
        element.innerHTML = originalContent;
        element.style.backgroundColor = originalBg;
        element.style.transform = 'scale(1)';
    }, 2000);
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? 'var(--success-500)' : 
                   type === 'error' ? 'var(--error-500)' : 'var(--primary-500)',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: 'var(--shadow-lg)',
        zIndex: '1000',
        opacity: '0',
        transform: 'translateX(100%)',
        transition: 'all 0.3s ease'
    });
    
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });
    
    // Animate out and remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// ===========================
// KEYBOARD SHORTCUTS
// ===========================

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (Elements.form && !AppState.isLoading) {
                Elements.form.dispatchEvent(new Event('submit'));
            }
        }
        
        // Ctrl/Cmd + R to reset (only when not on results)
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r') {
            const hasResults = document.querySelector('.results-section');
            if (!hasResults) {
                e.preventDefault();
                resetForm();
            }
        }
        
        // Escape to reset form
        if (e.key === 'Escape') {
            resetForm();
        }
        
        // Ctrl/Cmd + C when focused on results to copy summary
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c') {
            const resultsSection = document.querySelector('.results-section');
            if (resultsSection && document.activeElement.closest('.results-section')) {
                e.preventDefault();
                copyAllPoints();
            }
        }
    });
}

// ===========================
// PERFORMANCE OPTIMIZATION
// ===========================

// Debounce function for performance
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

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===========================
// ERROR HANDLING
// ===========================

window.addEventListener('error', (e) => {
    console.error('JavaScript Error:', e.error);
    // Could send error to analytics service here
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled Promise Rejection:', e.reason);
    // Could send error to analytics service here
});

// ===========================
// EXPORT FOR TESTING
// ===========================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AppState,
        Elements,
        isValidUrl,
        copyToClipboard,
        debounce,
        throttle
    };
}