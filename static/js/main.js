document.addEventListener('DOMContentLoaded', () => {
    // ==========================================================================
    // 1. Mobile Menu Navigation Toggle
    // ==========================================================================
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.className = 'fa-solid fa-xmark';
            } else {
                icon.className = 'fa-solid fa-bars';
            }
        });
    }

    // ==========================================================================
    // 2. Auto-close Toast Alerts
    // ==========================================================================
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            toast.style.transition = 'all 0.5s ease';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    });

    // ==========================================================================
    // 3. Multi-Step Form Logic (assess.html)
    // ==========================================================================
    const formSteps = document.querySelectorAll('.form-step-content');
    const stepNodes = document.querySelectorAll('.step-node');
    const progressBar = document.getElementById('stepProgressBar');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnSubmit = document.getElementById('btnSubmit');
    const assessmentForm = document.getElementById('assessmentForm');
    const loaderOverlay = document.getElementById('loaderOverlay');
    
    let currentStep = 0;
    
    // Check if we are on the form page
    if (formSteps.length > 0 && assessmentForm) {
        updateFormSteps();
        
        // Checkbox card toggle active classes
        const checkboxCards = document.querySelectorAll('.checkbox-card');
        checkboxCards.forEach(card => {
            const checkbox = card.querySelector('input[type="checkbox"]');
            
            // Sync initial state
            if (checkbox.checked) {
                card.classList.add('selected');
            }
            
            card.addEventListener('click', (e) => {
                // If the click wasn't directly on the checkbox, toggle it
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                }
                
                if (checkbox.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            });
        });

        // Navigation button listeners
        btnNext.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                currentStep++;
                updateFormSteps();
            }
        });
        
        btnPrev.addEventListener('click', () => {
            currentStep--;
            updateFormSteps();
        });
        
        // Show loading screen on valid submit
        assessmentForm.addEventListener('submit', (e) => {
            if (!validateStep(currentStep)) {
                e.preventDefault();
                return;
            }
            loaderOverlay.classList.add('active');
        });
    }

    function updateFormSteps() {
        formSteps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        stepNodes.forEach((node, index) => {
            if (index === currentStep) {
                node.className = 'step-node active';
            } else if (index < currentStep) {
                node.className = 'step-node completed';
            } else {
                node.className = 'step-node';
            }
        });
        
        // Progress bar width percentage
        const progressPercentage = (currentStep / (formSteps.length - 1)) * 80; // Scale to align with spacing
        if (progressBar) {
            progressBar.style.width = `${progressPercentage}%`;
        }
        
        // Button states
        if (currentStep === 0) {
            btnPrev.style.visibility = 'hidden';
            btnNext.style.display = 'inline-flex';
            btnSubmit.style.display = 'none';
        } else if (currentStep === formSteps.length - 1) {
            btnPrev.style.visibility = 'visible';
            btnNext.style.display = 'none';
            btnSubmit.style.display = 'inline-flex';
        } else {
            btnPrev.style.visibility = 'visible';
            btnNext.style.display = 'inline-flex';
            btnSubmit.style.display = 'none';
        }
    }

    function validateStep(stepIndex) {
        let isValid = true;
        clearErrors();
        
        if (stepIndex === 0) {
            // Step 1: Personal profile validation
            const nameInput = document.getElementById('name');
            const ageInput = document.getElementById('age');
            const genderInput = document.getElementById('gender');
            const incomeInput = document.getElementById('annual_income');
            const dependentsInput = document.getElementById('dependents');
            
            if (!nameInput.value.trim()) {
                showError(nameInput, 'Name is required.');
                isValid = false;
            }
            
            const age = parseInt(ageInput.value);
            if (isNaN(age) || age < 18 || age > 100) {
                showError(ageInput, 'Enter a valid age between 18 and 100.');
                isValid = false;
            }
            
            if (!genderInput.value) {
                showError(genderInput, 'Please select your gender.');
                isValid = false;
            }
            
            const income = parseFloat(incomeInput.value);
            if (isNaN(income) || income < 0) {
                showError(incomeInput, 'Enter a valid annual income (minimum 0).');
                isValid = false;
            }
            
            const dependents = parseInt(dependentsInput.value);
            if (isNaN(dependents) || dependents < 0 || dependents > 20) {
                showError(dependentsInput, 'Enter dependents between 0 and 20.');
                isValid = false;
            }
        } else if (stepIndex === 2) {
            // Step 3: Preferred plans checkbox check
            const checkboxes = document.querySelectorAll('input[name="preferences"]:checked');
            if (checkboxes.length === 0) {
                const checkContainer = document.querySelector('.checkbox-grid');
                showError(checkContainer, 'Please select at least one insurance preference.');
                isValid = false;
            }
        }
        
        return isValid;
    }

    function showError(element, message) {
        element.style.borderColor = 'var(--risk-high)';
        const formGroup = element.closest('.form-group');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'var(--risk-high)';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '0.5rem';
        errorDiv.style.fontWeight = '600';
        errorDiv.textContent = message;
        formGroup.appendChild(errorDiv);
    }

    function clearErrors() {
        const errors = document.querySelectorAll('.error-message');
        errors.forEach(e => e.remove());
        
        const inputs = document.querySelectorAll('.form-input, .form-select');
        inputs.forEach(input => {
            input.style.borderColor = 'var(--border-color)';
        });
    }

    // ==========================================================================
    // 4. Dashboard Gauge Animating Circle (dashboard.html)
    // ==========================================================================
    const riskGaugeNum = document.getElementById('riskGaugeNum');
    const riskCircleProgress = document.getElementById('riskCircleProgress');
    
    if (riskGaugeNum && riskCircleProgress) {
        const score = parseInt(riskGaugeNum.getAttribute('data-risk-score')) || 0;
        
        // Define Circle Circumference variables (radius r=90)
        const radius = 90;
        const circumference = 2 * Math.PI * radius; // ~565.48
        
        // Set stroke dasharray and offset
        riskCircleProgress.style.strokeDasharray = circumference;
        riskCircleProgress.style.strokeDashoffset = circumference;
        
        // Animate stroke color gradient states
        let strokeColor = 'var(--risk-low)';
        if (score > 65) {
            strokeColor = 'var(--risk-high)';
        } else if (score > 35) {
            strokeColor = 'var(--risk-med)';
        }
        
        riskCircleProgress.style.stroke = strokeColor;
        
        // Trigger drawing animation
        setTimeout(() => {
            const offset = circumference - (score / 100) * circumference;
            riskCircleProgress.style.strokeDashoffset = offset;
        }, 100);
        
        // Count up animation for number display
        let currentCount = 0;
        const duration = 1200; // ms
        const stepTime = Math.abs(Math.floor(duration / score));
        
        if (score > 0) {
            const timer = setInterval(() => {
                currentCount++;
                riskGaugeNum.textContent = currentCount;
                if (currentCount >= score) {
                    clearInterval(timer);
                }
            }, stepTime);
        } else {
            riskGaugeNum.textContent = '0';
        }
    }
});
