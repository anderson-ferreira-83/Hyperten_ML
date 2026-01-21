/**
 * AWS API Integration for Hypertension Prediction
 * Handles communication with the AWS Lambda API
 */

// API Configuration
const API_CONFIG = {
    baseUrl: 'https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com',
    endpoints: {
        predict: '/predict',
        health: '/health'
    },
    timeout: 10000 // 10 seconds
};

/**
 * Make a prediction request to the AWS API
 * @param {Object} patientData - Patient data for prediction
 * @returns {Promise<Object>} - Prediction result
 */
async function predictRisk(patientData) {
    const url = API_CONFIG.baseUrl + API_CONFIG.endpoints.predict;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(patientData),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;

    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('A requisição expirou. Por favor, tente novamente.');
        }
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Check API health status
 * @returns {Promise<Object>} - Health status
 */
async function checkApiHealth() {
    const url = API_CONFIG.baseUrl + API_CONFIG.endpoints.health;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            return { status: 'unhealthy', message: 'API not responding' };
        }

        const result = await response.json();
        return { status: 'healthy', data: result };

    } catch (error) {
        console.error('Health check error:', error);
        return { status: 'unhealthy', message: error.message };
    }
}

/**
 * Validate patient data before sending to API
 * @param {Object} data - Patient data to validate
 * @returns {Object} - Validation result
 */
function validatePatientData(data) {
    const errors = [];

    // Required fields
    const requiredFields = [
        'sexo', 'idade', 'fumante_atualmente', 'cigarros_por_dia',
        'medicamento_pressao', 'diabetes', 'colesterol_total',
        'pressao_sistolica', 'pressao_diastolica', 'imc',
        'frequencia_cardiaca', 'glicose'
    ];

    for (const field of requiredFields) {
        if (data[field] === undefined || data[field] === null || data[field] === '') {
            errors.push(`Campo obrigatório: ${field}`);
        }
    }

    // Range validations
    const ranges = {
        idade: { min: 18, max: 100 },
        pressao_sistolica: { min: 80, max: 220 },
        pressao_diastolica: { min: 50, max: 150 },
        imc: { min: 15, max: 50 },
        colesterol_total: { min: 100, max: 400 },
        glicose: { min: 50, max: 300 },
        frequencia_cardiaca: { min: 40, max: 150 },
        cigarros_por_dia: { min: 0, max: 60 }
    };

    for (const [field, range] of Object.entries(ranges)) {
        const value = data[field];
        if (value !== undefined && (value < range.min || value > range.max)) {
            errors.push(`${field} deve estar entre ${range.min} e ${range.max}`);
        }
    }

    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * Format API response for display
 * @param {Object} response - API response
 * @returns {Object} - Formatted response
 */
function formatApiResponse(response) {
    return {
        probability: response.probability || 0,
        prediction: response.prediction || 0,
        risk_category: getRiskCategory(response.probability || 0),
        model: response.model || 'RandomForestClassifier',
        model_version: response.model_version || 'rf_v1',
        confidence: getConfidenceLevel(response.probability || 0)
    };
}

/**
 * Get risk category based on probability
 * @param {number} probability - Risk probability (0-1)
 * @returns {string} - Risk category
 */
function getRiskCategory(probability) {
    if (probability < 0.3) return 'low';
    if (probability < 0.7) return 'medium';
    return 'high';
}

/**
 * Get confidence level description
 * @param {number} probability - Risk probability (0-1)
 * @returns {string} - Confidence description
 */
function getConfidenceLevel(probability) {
    // Distance from 0.5 indicates confidence
    const distance = Math.abs(probability - 0.5) * 2;

    if (distance > 0.8) return 'Muito Alta';
    if (distance > 0.6) return 'Alta';
    if (distance > 0.4) return 'Moderada';
    return 'Baixa';
}

/**
 * Create sample patient data for testing
 * @param {string} riskLevel - 'low', 'medium', or 'high'
 * @returns {Object} - Sample patient data
 */
function createSamplePatient(riskLevel = 'medium') {
    const samples = {
        low: {
            sexo: 0,
            idade: 35,
            fumante_atualmente: 0,
            cigarros_por_dia: 0,
            medicamento_pressao: 0,
            diabetes: 0,
            colesterol_total: 180,
            pressao_sistolica: 115,
            pressao_diastolica: 75,
            imc: 23,
            frequencia_cardiaca: 68,
            glicose: 85
        },
        medium: {
            sexo: 1,
            idade: 50,
            fumante_atualmente: 0,
            cigarros_por_dia: 0,
            medicamento_pressao: 0,
            diabetes: 0,
            colesterol_total: 220,
            pressao_sistolica: 135,
            pressao_diastolica: 88,
            imc: 27,
            frequencia_cardiaca: 75,
            glicose: 100
        },
        high: {
            sexo: 1,
            idade: 65,
            fumante_atualmente: 1,
            cigarros_por_dia: 20,
            medicamento_pressao: 1,
            diabetes: 1,
            colesterol_total: 280,
            pressao_sistolica: 160,
            pressao_diastolica: 100,
            imc: 32,
            frequencia_cardiaca: 90,
            glicose: 140
        }
    };

    return samples[riskLevel] || samples.medium;
}

// Export functions for use in other scripts
window.predictRisk = predictRisk;
window.checkApiHealth = checkApiHealth;
window.validatePatientData = validatePatientData;
window.formatApiResponse = formatApiResponse;
window.createSamplePatient = createSamplePatient;
