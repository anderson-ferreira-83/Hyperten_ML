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
    valueDisplay.textContent = Number(slider.value).toFixed(decimals);
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

// Helper: Random integer between min and max (inclusive)
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Helper: Random float between min and max
function randFloat(min, max, decimals = 1) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}

// Generate random patient data
function generateRandomData() {
  // Categorical variables (random 0 or 1)
  const sexo = Math.random() > 0.5 ? 1 : 0;
  const fumante = Math.random() > 0.7 ? 1 : 0; // 30% chance of smoker
  const medicamento = Math.random() > 0.85 ? 1 : 0; // 15% chance
  const diabetes = Math.random() > 0.9 ? 1 : 0; // 10% chance

  // Continuous variables (realistic ranges)
  const idade = randInt(25, 80);
  const cigarros = fumante ? randInt(5, 30) : 0;
  const pressaoSist = randInt(100, 180);
  const pressaoDiast = randInt(65, 110);
  const freqCardiaca = randInt(55, 100);
  const imc = randFloat(19, 38, 1);
  const colesterol = randInt(150, 300);
  const glicose = randInt(70, 180);

  return {
    sexo,
    fumante_atualmente: fumante,
    medicamento_pressao: medicamento,
    diabetes,
    idade,
    cigarros_por_dia: cigarros,
    pressao_sistolica: pressaoSist,
    pressao_diastolica: pressaoDiast,
    frequencia_cardiaca: freqCardiaca,
    imc,
    colesterol_total: colesterol,
    glicose
  };
}

// Fill form with random data
document.getElementById('fill-demo').addEventListener('click', () => {
  const data = generateRandomData();

  // Set categorical radio buttons
  document.getElementById(data.sexo === 1 ? 'sexo-m' : 'sexo-f').checked = true;
  document.getElementById(data.fumante_atualmente === 1 ? 'fumante-s' : 'fumante-n').checked = true;
  document.getElementById(data.medicamento_pressao === 1 ? 'med-s' : 'med-n').checked = true;
  document.getElementById(data.diabetes === 1 ? 'diab-s' : 'diab-n').checked = true;

  // Enable/disable cigarettes based on smoker status
  if (data.fumante_atualmente === 1) {
    cigarrosSlider.disabled = false;
  } else {
    cigarrosSlider.disabled = true;
  }

  // Set slider values
  const sliderData = {
    idade: data.idade,
    cigarros_por_dia: data.cigarros_por_dia,
    pressao_sistolica: data.pressao_sistolica,
    pressao_diastolica: data.pressao_diastolica,
    frequencia_cardiaca: data.frequencia_cardiaca,
    imc: data.imc,
    colesterol_total: data.colesterol_total,
    glicose: data.glicose
  };

  sliders.forEach(({ id, decimals }) => {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);
    if (slider && sliderData[id] !== undefined) {
      slider.value = sliderData[id];
      valueDisplay.textContent = Number(sliderData[id]).toFixed(decimals);
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
  if (prob < 0.3) return '#10b981';
  if (prob < 0.7) return '#f59e0b';
  return '#ef4444';
}

// Get risk category based on probability
function getRiskCategory(prob) {
  if (prob < 0.3) return 'low';
  if (prob < 0.7) return 'medium';
  return 'high';
}

// Get risk category info
function getRiskInfo(category) {
  const info = {
    low: {
      text: 'Risco Baixo',
      icon: '&#10003;',
      description: 'Baixa probabilidade de hipertensao. Manter habitos saudaveis e acompanhamento de rotina.'
    },
    medium: {
      text: 'Risco Moderado',
      icon: '&#9888;',
      description: 'Fatores de risco presentes. Atencao aos habitos de vida e acompanhamento medico mais frequente.'
    },
    high: {
      text: 'Risco Elevado',
      icon: '&#9888;',
      description: 'Alta probabilidade de hipertensao. Avaliacao medica imediata e intervencao nos fatores de risco.'
    }
  };
  return info[category] || info.medium;
}

// Generate clinical interpretation
function getInterpretation(prob, prediction, data) {
  const probPercent = (prob * 100).toFixed(1);
  let text = `Probabilidade estimada de ${probPercent}% para hipertensao. `;

  const riskFactors = [];
  if (data.idade >= 60) riskFactors.push('idade avancada');
  if (data.fumante_atualmente === 1) riskFactors.push('tabagismo');
  if (data.diabetes === 1) riskFactors.push('diabetes');
  if (data.medicamento_pressao === 1) riskFactors.push('uso de anti-hipertensivo');
  if (data.pressao_sistolica >= 140) riskFactors.push('PA sistolica elevada');
  if (data.pressao_diastolica >= 90) riskFactors.push('PA diastolica elevada');
  if (data.imc >= 30) riskFactors.push('obesidade');
  if (data.colesterol_total >= 240) riskFactors.push('colesterol elevado');
  if (data.glicose >= 126) riskFactors.push('glicose elevada');

  if (riskFactors.length > 0) {
    text += `Fatores identificados: ${riskFactors.join(', ')}.`;
  } else {
    text += 'Nenhum fator de risco significativo identificado.';
  }

  return text;
}

// Form submission
form.addEventListener('submit', async (e) => {
  e.preventDefault();

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
  const category = getRiskCategory(prob);
  const riskInfo = getRiskInfo(category);

  resultContainer.style.display = 'none';
  resultContent.style.display = 'block';

  probValue.textContent = `${probPercent}%`;
  probValue.style.color = getRiskColor(prob);

  probBar.style.width = `${prob * 100}%`;
  probMarker.style.left = `${prob * 100}%`;

  riskBadge.className = `risk-badge ${category}`;
  riskIcon.innerHTML = riskInfo.icon;
  riskText.textContent = riskInfo.text;
  riskDescription.textContent = riskInfo.description;

  modelName.textContent = result.model_selected || result.model || 'N/A';
  thresholdValue.textContent = result.threshold ? result.threshold.toFixed(2) : 'N/A';
  thresholdProfile.textContent = result.threshold_profile || 'N/A';
  predictionValue.textContent = result.prediction === 1 ? 'Positivo (1)' : 'Negativo (0)';

  interpretationText.textContent = getInterpretation(prob, result.prediction, inputData);
}
