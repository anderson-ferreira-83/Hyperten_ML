// API Configuration - Auto-detect local vs production
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = isLocal
  ? `${window.location.protocol}//${window.location.host}`
  : 'https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com';
const API_URL = `${API_BASE}/predict?threshold_key=balanced`;

// DOM Elements
const form = document.getElementById('predict-form');
const resultContainer = document.getElementById('result-container');
const resultContent = document.getElementById('result-content');

// Result Elements
const probValue = document.getElementById('prob-value');
const probBar = document.getElementById('prob-bar');
const probMarker = document.getElementById('prob-marker');
const riskBadge = document.getElementById('risk-badge');
const riskIcon = document.getElementById('risk-icon');
const riskText = document.getElementById('risk-text');
const riskDescription = document.getElementById('risk-description');
const modelName = document.getElementById('model-name');
const thresholdValue = document.getElementById('threshold-value');
const thresholdProfile = document.getElementById('threshold-profile');
const predictionValue = document.getElementById('prediction-value');
const interpretationText = document.getElementById('interpretation-text');

// Slider Configuration
const sliders = [
  { id: 'idade', decimals: 0 },
  { id: 'cigarros_por_dia', decimals: 0 },
  { id: 'pressao_sistolica', decimals: 0 },
  { id: 'pressao_diastolica', decimals: 0 },
  { id: 'frequencia_cardiaca', decimals: 0 },
  { id: 'imc', decimals: 1 },
  { id: 'colesterol_total', decimals: 0 },
  { id: 'glicose', decimals: 0 }
];

// Initialize sliders
sliders.forEach(({ id, decimals }) => {
  const slider = document.getElementById(id);
  const valueDisplay = document.getElementById(`${id}-value`);

  if (slider && valueDisplay) {
    // Set initial value
    valueDisplay.textContent = Number(slider.value).toFixed(decimals);

    // Update on input
    slider.addEventListener('input', () => {
      valueDisplay.textContent = Number(slider.value).toFixed(decimals);
    });
  }
});

// Smoker toggle - enable/disable cigarettes slider
const smokerRadios = document.querySelectorAll('input[name="fumante_atualmente"]');
const cigarrosSlider = document.getElementById('cigarros_por_dia');
const cigarrosValue = document.getElementById('cigarros_por_dia-value');

function toggleCigarros() {
  const isSmoker = document.querySelector('input[name="fumante_atualmente"]:checked').value === '1';

  if (isSmoker) {
    cigarrosSlider.disabled = false;
  } else {
    cigarrosSlider.disabled = true;
    cigarrosSlider.value = 0;
    cigarrosValue.textContent = '0';
  }
}

smokerRadios.forEach(radio => {
  radio.addEventListener('change', toggleCigarros);
});

// Fill demo data
document.getElementById('fill-demo').addEventListener('click', () => {
  const demoData = {
    'sexo-m': true,
    idade: 55,
    'fumante-s': true,
    cigarros_por_dia: 10,
    'med-s': true,
    'diab-n': true,
    colesterol_total: 250,
    pressao_sistolica: 150,
    pressao_diastolica: 95,
    imc: 28.5,
    frequencia_cardiaca: 82,
    glicose: 110
  };

  // Set radio buttons
  document.getElementById('sexo-m').checked = true;
  document.getElementById('fumante-s').checked = true;
  document.getElementById('med-s').checked = true;
  document.getElementById('diab-n').checked = true;

  // Enable cigarettes slider
  cigarrosSlider.disabled = false;

  // Set slider values
  sliders.forEach(({ id, decimals }) => {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);
    if (slider && demoData[id] !== undefined) {
      slider.value = demoData[id];
      valueDisplay.textContent = Number(demoData[id]).toFixed(decimals);
    }
  });
});

// Reset form
document.getElementById('reset-form').addEventListener('click', () => {
  // Reset radio buttons to defaults
  document.getElementById('sexo-f').checked = true;
  document.getElementById('fumante-n').checked = true;
  document.getElementById('med-n').checked = true;
  document.getElementById('diab-n').checked = true;

  // Reset sliders to default values
  const defaults = {
    idade: 50,
    cigarros_por_dia: 0,
    pressao_sistolica: 120,
    pressao_diastolica: 80,
    frequencia_cardiaca: 72,
    imc: 25,
    colesterol_total: 200,
    glicose: 90
  };

  sliders.forEach(({ id, decimals }) => {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);
    if (slider && defaults[id] !== undefined) {
      slider.value = defaults[id];
      valueDisplay.textContent = Number(defaults[id]).toFixed(decimals);
    }
  });

  // Disable cigarettes slider
  cigarrosSlider.disabled = true;

  // Hide results
  resultContainer.style.display = 'block';
  resultContent.style.display = 'none';
});

// Get risk color based on probability
function getRiskColor(prob) {
  if (prob < 0.3) return '#10b981'; // green
  if (prob < 0.7) return '#f59e0b'; // yellow
  return '#ef4444'; // red
}

// Get risk category info
function getRiskInfo(category, prob) {
  const info = {
    low: {
      text: 'Risco Baixo',
      icon: '&#10003;', // checkmark
      description: 'O paciente apresenta baixa probabilidade de desenvolver hipertensao. Recomenda-se manter habitos saudaveis e realizar acompanhamento de rotina.'
    },
    medium: {
      text: 'Risco Moderado',
      icon: '&#9888;', // warning
      description: 'O paciente apresenta risco moderado. Recomenda-se atencao aos fatores de risco modificaveis e acompanhamento medico mais frequente.'
    },
    high: {
      text: 'Risco Elevado',
      icon: '&#9888;', // warning
      description: 'O paciente apresenta alta probabilidade de hipertensao. Recomenda-se avaliacao medica imediata e intervencao nos fatores de risco.'
    }
  };

  return info[category] || info.medium;
}

// Generate clinical interpretation
function getInterpretation(prob, prediction, data) {
  const probPercent = (prob * 100).toFixed(1);
  let text = `Com base nos dados fornecidos, o modelo estima uma probabilidade de ${probPercent}% para hipertensao. `;

  // Add risk factors analysis
  const riskFactors = [];

  if (data.idade >= 60) riskFactors.push('idade avancada');
  if (data.fumante_atualmente === 1) riskFactors.push('tabagismo');
  if (data.diabetes === 1) riskFactors.push('diabetes');
  if (data.medicamento_pressao === 1) riskFactors.push('uso de medicamento para pressao');
  if (data.pressao_sistolica >= 140) riskFactors.push('pressao sistolica elevada');
  if (data.pressao_diastolica >= 90) riskFactors.push('pressao diastolica elevada');
  if (data.imc >= 30) riskFactors.push('obesidade');
  if (data.colesterol_total >= 240) riskFactors.push('colesterol elevado');
  if (data.glicose >= 126) riskFactors.push('glicose elevada');

  if (riskFactors.length > 0) {
    text += `Fatores de risco identificados: ${riskFactors.join(', ')}. `;
  } else {
    text += 'Nenhum fator de risco significativo identificado nos dados fornecidos. ';
  }

  if (prediction === 1) {
    text += 'Recomenda-se avaliacao medica para confirmacao diagnostica.';
  } else {
    text += 'Manter acompanhamento de rotina e habitos de vida saudaveis.';
  }

  return text;
}

// Form submission
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Collect form data
  const data = {
    sexo: Number(document.querySelector('input[name="sexo"]:checked').value),
    idade: Number(document.getElementById('idade').value),
    fumante_atualmente: Number(document.querySelector('input[name="fumante_atualmente"]:checked').value),
    cigarros_por_dia: Number(document.getElementById('cigarros_por_dia').value),
    medicamento_pressao: Number(document.querySelector('input[name="medicamento_pressao"]:checked').value),
    diabetes: Number(document.querySelector('input[name="diabetes"]:checked').value),
    colesterol_total: Number(document.getElementById('colesterol_total').value),
    pressao_sistolica: Number(document.getElementById('pressao_sistolica').value),
    pressao_diastolica: Number(document.getElementById('pressao_diastolica').value),
    imc: Number(document.getElementById('imc').value),
    frequencia_cardiaca: Number(document.getElementById('frequencia_cardiaca').value),
    glicose: Number(document.getElementById('glicose').value)
  };

  // Show loading state
  form.classList.add('loading');
  resultContainer.style.display = 'block';
  resultContent.style.display = 'none';
  resultContainer.innerHTML = '<div class="result-waiting"><div class="waiting-icon">&#8987;</div><p>Calculando...</p></div>';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro na API');
    }

    const result = await response.json();

    // Update UI with results
    displayResults(result, data);

  } catch (error) {
    resultContainer.innerHTML = `<div class="error-message">Erro: ${error.message}</div>`;
  } finally {
    form.classList.remove('loading');
  }
});

// Display results
function displayResults(result, inputData) {
  const prob = result.probability || 0;
  const probPercent = (prob * 100).toFixed(1);
  const category = result.risk_category || 'medium';
  const riskInfo = getRiskInfo(category, prob);

  // Hide waiting, show content
  resultContainer.style.display = 'none';
  resultContent.style.display = 'block';

  // Update probability display
  probValue.textContent = `${probPercent}%`;
  probValue.style.color = getRiskColor(prob);

  // Update probability bar
  probBar.style.width = `${prob * 100}%`;
  probMarker.style.left = `${prob * 100}%`;

  // Update risk badge
  riskBadge.className = `risk-badge ${category}`;
  riskIcon.innerHTML = riskInfo.icon;
  riskText.textContent = riskInfo.text;
  riskDescription.textContent = riskInfo.description;

  // Update technical details
  modelName.textContent = result.model_selected || result.model || 'N/A';
  thresholdValue.textContent = result.threshold ? result.threshold.toFixed(2) : 'N/A';
  thresholdProfile.textContent = result.threshold_profile || 'N/A';
  predictionValue.textContent = result.prediction === 1 ? 'Positivo (1)' : 'Negativo (0)';

  // Update interpretation
  interpretationText.textContent = getInterpretation(prob, result.prediction, inputData);
}
