const API_URL = '/predict?threshold_key=balanced';

const form = document.getElementById('predict-form');
const scoreEl = document.getElementById('score');
const detailsEl = document.getElementById('details');
const modelEl = document.getElementById('model-info');
const riskEl = document.getElementById('risk');
const smokerEl = document.getElementById('fumante_atualmente');
const cigsEl = document.getElementById('cigarros_por_dia');

const toggleCigsBySmoker = () => {
  const isSmoker = Number(smokerEl.value) === 1;
  if (!isSmoker) {
    cigsEl.value = 0;
    cigsEl.setAttribute('disabled', 'disabled');
  } else {
    cigsEl.removeAttribute('disabled');
  }
};

toggleCigsBySmoker();
smokerEl.addEventListener('change', toggleCigsBySmoker);

document.getElementById('fill-demo').addEventListener('click', () => {
  const demo = {
    sexo: 1,
    idade: 55,
    fumante_atualmente: 0,
    cigarros_por_dia: 0,
    medicamento_pressao: 0,
    diabetes: 0,
    colesterol_total: 220,
    pressao_sistolica: 140,
    pressao_diastolica: 90,
    imc: 27.5,
    frequencia_cardiaca: 78,
    glicose: 90
  };
  Object.entries(demo).forEach(([k, v]) => {
    const el = document.getElementById(k);
    if (el) el.value = v;
  });
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());

  for (const k in data) {
    data[k] = data[k] === '' ? null : Number(data[k]);
  }

  scoreEl.textContent = '...';
  detailsEl.textContent = 'Calculando...';
  if (modelEl) modelEl.textContent = 'Modelo: ...';
  riskEl.textContent = '';

  const rangeErrors = [];
  const fieldErrors = {};
  const numericInputs = form.querySelectorAll('input[type="number"]');
  numericInputs.forEach((input) => {
    const value = input.value === '' ? null : Number(input.value);
    if (value === null) return;
    const min = input.getAttribute('min');
    const max = input.getAttribute('max');
    if (min !== null && value < Number(min)) {
      const label = form.querySelector(`label[for="${input.id}"]`);
      const msg = `${label ? label.textContent : input.id} abaixo do minimo (${min}).`;
      rangeErrors.push(msg);
      fieldErrors[input.id] = msg;
    }
    if (max !== null && value > Number(max)) {
      const label = form.querySelector(`label[for="${input.id}"]`);
      const msg = `${label ? label.textContent : input.id} acima do maximo (${max}).`;
      rangeErrors.push(msg);
      fieldErrors[input.id] = msg;
    }
  });

  document.querySelectorAll('.error').forEach((el) => el.remove());
  numericInputs.forEach((input) => input.classList.remove('invalid'));

  Object.entries(fieldErrors).forEach(([id, msg]) => {
    const input = document.getElementById(id);
    if (!input) return;
    input.classList.add('invalid');
    const error = document.createElement('div');
    error.className = 'error';
    error.textContent = msg;
    input.insertAdjacentElement('afterend', error);
  });

  if (rangeErrors.length > 0) {
    scoreEl.textContent = '--';
    detailsEl.textContent = rangeErrors.join(' ');
    riskEl.textContent = '';
    return;
  }

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro na API');
    }

    const payload = await res.json();
    const prob = payload.probability ?? 0;
    const label = payload.prediction === 1 ? 'Alto risco' : 'Baixo risco';
    const modelName = payload.model_selected || payload.model || 'Nao informado';

    scoreEl.textContent = `${(prob * 100).toFixed(1)}%`;
    detailsEl.textContent = `Threshold: ${payload.threshold} | Perfil: ${payload.threshold_profile}`;
    if (modelEl) modelEl.textContent = `Modelo: ${modelName}`;
    riskEl.textContent = label;
  } catch (err) {
    scoreEl.textContent = '--';
    detailsEl.textContent = err.message;
    if (modelEl) modelEl.textContent = 'Modelo: --';
    riskEl.textContent = '';
  }
});
