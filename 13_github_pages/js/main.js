/**
 * Main JavaScript for Hypertension Prediction TCC
 * Handles UI interactions and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for navigation links
    initSmoothScroll();

    // Navbar scroll effect
    initNavbarScroll();

    // Animate elements on scroll
    initScrollAnimations();

    // Initialize demo form
    initDemoForm();
});

/**
 * Smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Navbar background change on scroll
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        }
    });
}

/**
 * Animate elements when they come into view
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and figures
    document.querySelectorAll('.problem-card, .pipeline-step, .result-card, .figure-card, .threshold-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Add animation class styles
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

/**
 * Initialize demo form interactions
 */
function initDemoForm() {
    const predictBtn = document.getElementById('predictBtn');

    if (predictBtn) {
        predictBtn.addEventListener('click', handlePrediction);
    }

    // Add input validation
    const inputs = document.querySelectorAll('.demo-form input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateInput(this);
        });
    });
}

/**
 * Validate numeric inputs
 */
function validateInput(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);

    if (value < min) {
        input.value = min;
    } else if (value > max) {
        input.value = max;
    }
}

/**
 * Handle prediction button click
 */
async function handlePrediction() {
    const btn = document.getElementById('predictBtn');
    const resultPanel = document.getElementById('resultPanel');
    const placeholder = resultPanel.querySelector('.result-placeholder');
    const resultContent = resultPanel.querySelector('.result-content');

    // Show loading state
    btn.disabled = true;
    btn.textContent = 'Calculando...';
    btn.classList.add('loading');

    try {
        // Collect form data
        const formData = collectFormData();

        // Call AWS API
        const result = await predictRisk(formData);

        // Display result
        displayResult(result);

        // Show result content
        placeholder.style.display = 'none';
        resultContent.style.display = 'block';

    } catch (error) {
        console.error('Prediction error:', error);
        alert('Erro ao calcular risco. Por favor, tente novamente ou acesse a demo completa na AWS.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Calcular Risco';
        btn.classList.remove('loading');
    }
}

/**
 * Collect form data
 */
function collectFormData() {
    return {
        sexo: parseInt(document.getElementById('sexo').value),
        idade: parseInt(document.getElementById('idade').value),
        fumante_atualmente: parseInt(document.getElementById('fumante_atualmente').value),
        cigarros_por_dia: parseInt(document.getElementById('cigarros_por_dia').value),
        medicamento_pressao: parseInt(document.getElementById('medicamento_pressao').value),
        diabetes: parseInt(document.getElementById('diabetes').value),
        colesterol_total: parseInt(document.getElementById('colesterol_total').value),
        pressao_sistolica: parseInt(document.getElementById('pressao_sistolica').value),
        pressao_diastolica: parseInt(document.getElementById('pressao_diastolica').value),
        imc: parseFloat(document.getElementById('imc').value),
        frequencia_cardiaca: parseInt(document.getElementById('frequencia_cardiaca').value),
        glicose: parseInt(document.getElementById('glicose').value)
    };
}

/**
 * Display prediction result
 */
function displayResult(result) {
    const gaugeValue = document.getElementById('gaugeValue');
    const riskCategory = document.getElementById('riskCategory');
    const riskDetails = document.getElementById('riskDetails');

    // Format probability
    const probability = (result.probability * 100).toFixed(1);
    gaugeValue.textContent = probability + '%';

    // Set category
    let categoryText = '';
    let categoryClass = '';

    if (result.risk_category === 'low' || probability < 30) {
        categoryText = 'Baixo Risco';
        categoryClass = 'low';
    } else if (result.risk_category === 'medium' || probability < 70) {
        categoryText = 'Risco Moderado';
        categoryClass = 'medium';
    } else {
        categoryText = 'Alto Risco';
        categoryClass = 'high';
    }

    riskCategory.textContent = categoryText;
    riskCategory.className = 'risk-category ' + categoryClass;

    // Set details
    riskDetails.innerHTML = `
        <p><strong>Modelo:</strong> ${result.model || 'Random Forest'}</p>
        <p><strong>Versão:</strong> ${result.model_version || 'rf_v1'}</p>
        <p><strong>Predição:</strong> ${result.prediction === 1 ? 'Positivo para risco' : 'Negativo para risco'}</p>
    `;

    // Animate gauge
    animateGauge(probability);
}

/**
 * Animate the gauge value
 */
function animateGauge(targetValue) {
    const gaugeValue = document.getElementById('gaugeValue');
    let currentValue = 0;
    const duration = 1000;
    const steps = 60;
    const increment = targetValue / steps;
    const stepDuration = duration / steps;

    const animation = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(animation);
        }
        gaugeValue.textContent = currentValue.toFixed(1) + '%';
    }, stepDuration);
}

/**
 * Format number with locale
 */
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR').format(num);
}
