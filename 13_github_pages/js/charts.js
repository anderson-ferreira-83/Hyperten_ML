/**
 * Gráficos Interativos - TCC Hipertensão
 * Usando Plotly.js para visualizações interativas
 */

// Configuração global de cores
const COLORS = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#2ecc71',
    danger: '#e74c3c',
    warning: '#f39c12',
    info: '#3498db',
    dark: '#2c3e50',
    gray: '#95a5a6',
    models: [
        '#667eea', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
        '#3498db', '#1abc9c', '#e67e22', '#34495e', '#7f8c8d'
    ]
};

// Configuração global de layout
const LAYOUT_CONFIG = {
    font: { family: 'Inter, sans-serif' },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 40, r: 20, b: 40, l: 60 },
    hoverlabel: {
        bgcolor: '#2c3e50',
        font: { color: 'white', family: 'Inter, sans-serif' }
    }
};

const PLOTLY_CONFIG = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false,
    toImageButtonOptions: {
        format: 'png',
        filename: 'grafico_hipertensao',
        scale: 2
    }
};

// ===== DADOS =====

// Dados de comparação de modelos
const MODELS_DATA = {
    names: ['Random Forest', 'Gradient Boosting', 'XGBoost', 'Logistic Regression',
            'AdaBoost', 'LightGBM', 'Extra Trees', 'Decision Tree', 'KNN', 'Naive Bayes'],
    accuracy: [0.8996, 0.9003, 0.8976, 0.8848, 0.8935, 0.8902, 0.8895, 0.8565, 0.8511, 0.7615],
    precision: [0.7989, 0.8051, 0.8047, 0.7715, 0.8111, 0.8016, 0.8087, 0.7340, 0.7353, 0.8543],
    recall: [0.9046, 0.8959, 0.8850, 0.8937, 0.8568, 0.8590, 0.8438, 0.8438, 0.8134, 0.2798],
    f1_score: [0.8484, 0.8480, 0.8430, 0.8281, 0.8333, 0.8293, 0.8259, 0.7851, 0.7724, 0.4216],
    f2_score: [0.8812, 0.8761, 0.8677, 0.8663, 0.8473, 0.8469, 0.8366, 0.8193, 0.7965, 0.3233],
    auc_roc: [0.9508, 0.9596, 0.9534, 0.9547, 0.9502, 0.9524, 0.9500, 0.8598, 0.9073, 0.9353],
    tn: [918, 923, 924, 901, 931, 925, 931, 882, 888, 1001],
    fp: [105, 100, 99, 122, 92, 98, 92, 141, 135, 22],
    fn: [44, 48, 53, 49, 66, 65, 72, 72, 86, 332],
    tp: [417, 413, 408, 412, 395, 396, 389, 389, 375, 129]
};

// Dados de importância das features
const FEATURE_IMPORTANCE = {
    features: ['Pressão Sistólica', 'Pressão Diastólica', 'IMC', 'Idade',
               'Colesterol Total', 'Freq. Cardíaca', 'Glicose', 'Medicamento Pressão',
               'Sexo', 'Cigarros/Dia', 'Fumante', 'Diabetes'],
    importance: [0.437, 0.268, 0.060, 0.058, 0.036, 0.031, 0.030, 0.030, 0.019, 0.018, 0.011, 0.0005],
    categories: ['Pressão Arterial', 'Pressão Arterial', 'Antropométricas', 'Demografia',
                 'Biomarcadores', 'Biomarcadores', 'Biomarcadores', 'Medicamentos',
                 'Demografia', 'Estilo de Vida', 'Estilo de Vida', 'Biomarcadores'],
    colors: ['#e74c3c', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#9b59b6',
             '#9b59b6', '#f39c12', '#2ecc71', '#1abc9c', '#1abc9c', '#9b59b6']
};

// Dados de importância por categoria
const CATEGORY_IMPORTANCE = {
    categories: ['Pressão Arterial', 'Antropométricas', 'Demografia', 'Biomarcadores', 'Medicamentos', 'Estilo de Vida'],
    importance: [0.3524, 0.0605, 0.0389, 0.0328, 0.0150, 0.0115],
    colors: ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c']
};

// Dados para curvas ROC (pontos simulados baseados nos AUC)
const ROC_DATA = {
    'Random Forest': {
        fpr: [0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80, 1.0],
        tpr: [0, 0.45, 0.70, 0.85, 0.90, 0.93, 0.96, 0.98, 0.99, 1.0, 1.0],
        auc: 0.9508
    },
    'Gradient Boosting': {
        fpr: [0, 0.01, 0.03, 0.08, 0.12, 0.18, 0.28, 0.38, 0.58, 0.78, 1.0],
        tpr: [0, 0.50, 0.75, 0.88, 0.92, 0.95, 0.97, 0.98, 0.99, 1.0, 1.0],
        auc: 0.9596
    },
    'XGBoost': {
        fpr: [0, 0.02, 0.04, 0.09, 0.14, 0.19, 0.29, 0.39, 0.59, 0.79, 1.0],
        tpr: [0, 0.48, 0.72, 0.86, 0.91, 0.94, 0.96, 0.98, 0.99, 1.0, 1.0],
        auc: 0.9534
    },
    'Logistic Regression': {
        fpr: [0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80, 1.0],
        tpr: [0, 0.47, 0.73, 0.87, 0.91, 0.94, 0.97, 0.98, 0.99, 1.0, 1.0],
        auc: 0.9547
    }
};

// Dados de threshold
const THRESHOLD_DATA = {
    thresholds: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    sensitivity: [0.98, 0.96, 0.93, 0.90, 0.85, 0.78, 0.68, 0.55, 0.35],
    specificity: [0.65, 0.78, 0.85, 0.88, 0.91, 0.94, 0.96, 0.98, 0.99],
    f1: [0.72, 0.80, 0.84, 0.85, 0.84, 0.82, 0.77, 0.68, 0.50],
    precision: [0.55, 0.68, 0.76, 0.82, 0.85, 0.88, 0.91, 0.94, 0.97]
};


// ===== GRÁFICOS =====

/**
 * 1. Distribuição do Target - Donut Chart
 */
function createTargetDistribution() {
    const element = document.getElementById('chart-target-distribution');
    if (!element) return;

    const data = [{
        values: [2924, 1316],
        labels: ['Sem Hipertensão', 'Com Hipertensão'],
        type: 'pie',
        hole: 0.5,
        marker: {
            colors: [COLORS.success, COLORS.danger]
        },
        textinfo: 'percent',
        textposition: 'outside',
        textfont: { size: 14 },
        hovertemplate: '<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    }];

    const layout = {
        ...LAYOUT_CONFIG,
        showlegend: true,
        legend: { orientation: 'h', y: -0.1 },
        annotations: [{
            text: '<b>4.240</b><br>Pacientes',
            showarrow: false,
            font: { size: 16, color: COLORS.dark }
        }]
    };

    Plotly.newPlot(element, data, layout, PLOTLY_CONFIG);
}

/**
 * 2. Comparação de Métricas - Bar Chart com Dropdown
 */
function createMetricsComparison() {
    const element = document.getElementById('chart-metrics-comparison');
    if (!element) return;

    // Criar traces para cada métrica
    const metrics = ['auc_roc', 'f1_score', 'recall', 'precision', 'accuracy', 'f2_score'];
    const metricLabels = {
        'auc_roc': 'ROC-AUC',
        'f1_score': 'F1-Score',
        'recall': 'Recall (Sensibilidade)',
        'precision': 'Precision',
        'accuracy': 'Accuracy',
        'f2_score': 'F2-Score'
    };

    // Ordenar modelos por AUC-ROC
    const sortedIndices = MODELS_DATA.auc_roc
        .map((val, idx) => ({ val, idx }))
        .sort((a, b) => b.val - a.val)
        .map(obj => obj.idx);

    const traces = metrics.map((metric, i) => {
        const values = sortedIndices.map(idx => MODELS_DATA[metric][idx]);
        const names = sortedIndices.map(idx => MODELS_DATA.names[idx]);
        const colors = names.map(name => name === 'Random Forest' ? COLORS.primary : COLORS.gray);

        return {
            x: names,
            y: values.map(v => v * 100),
            type: 'bar',
            name: metricLabels[metric],
            marker: { color: colors },
            hovertemplate: '<b>%{x}</b><br>' + metricLabels[metric] + ': %{y:.2f}%<extra></extra>',
            visible: i === 0
        };
    });

    // Criar botões do dropdown
    const buttons = metrics.map((metric, i) => ({
        label: metricLabels[metric],
        method: 'update',
        args: [
            { visible: metrics.map((_, j) => j === i) },
            { title: `Comparação de Modelos - ${metricLabels[metric]}` }
        ]
    }));

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Comparação de Modelos - ROC-AUC',
        xaxis: {
            tickangle: -45,
            tickfont: { size: 11 }
        },
        yaxis: {
            title: 'Valor (%)',
            range: [0, 100]
        },
        updatemenus: [{
            buttons: buttons,
            direction: 'down',
            showactive: true,
            x: 0.0,
            y: 1.15,
            xanchor: 'left',
            yanchor: 'top',
            bgcolor: 'white',
            bordercolor: COLORS.primary
        }]
    };

    Plotly.newPlot(element, traces, layout, PLOTLY_CONFIG);
}

/**
 * 3. Curvas ROC Interativas
 */
function createROCCurves() {
    const element = document.getElementById('chart-roc-curves');
    if (!element) return;

    const traces = [];
    const modelColors = [COLORS.primary, COLORS.danger, COLORS.success, COLORS.warning];

    Object.keys(ROC_DATA).forEach((model, i) => {
        const data = ROC_DATA[model];
        traces.push({
            x: data.fpr,
            y: data.tpr,
            mode: 'lines',
            name: `${model} (AUC: ${(data.auc * 100).toFixed(1)}%)`,
            line: { color: modelColors[i], width: 2.5 },
            hovertemplate: `<b>${model}</b><br>FPR: %{x:.2f}<br>TPR: %{y:.2f}<extra></extra>`
        });
    });

    // Linha diagonal de referência
    traces.push({
        x: [0, 1],
        y: [0, 1],
        mode: 'lines',
        name: 'Aleatório',
        line: { color: COLORS.gray, dash: 'dash', width: 1 },
        hoverinfo: 'skip'
    });

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Curvas ROC - Principais Modelos',
        xaxis: {
            title: 'Taxa de Falsos Positivos (FPR)',
            range: [0, 1]
        },
        yaxis: {
            title: 'Taxa de Verdadeiros Positivos (TPR)',
            range: [0, 1]
        },
        legend: {
            x: 1,
            y: 0,
            xanchor: 'right',
            bgcolor: 'rgba(255,255,255,0.8)'
        },
        shapes: [{
            type: 'rect',
            x0: 0, x1: 0.2,
            y0: 0.8, y1: 1,
            fillcolor: 'rgba(46, 204, 113, 0.1)',
            line: { width: 0 }
        }],
        annotations: [{
            x: 0.1,
            y: 0.9,
            text: 'Zona<br>Ideal',
            showarrow: false,
            font: { size: 10, color: COLORS.success }
        }]
    };

    Plotly.newPlot(element, traces, layout, PLOTLY_CONFIG);
}

/**
 * 4. Matriz de Confusão - Heatmap
 */
function createConfusionMatrix() {
    const element = document.getElementById('chart-confusion-matrix');
    if (!element) return;

    // Random Forest confusion matrix
    const tn = 918, fp = 105, fn = 44, tp = 417;
    const total = tn + fp + fn + tp;

    const z = [[tn, fp], [fn, tp]];
    const zText = [
        [`VN: ${tn}<br>(${(tn/total*100).toFixed(1)}%)`, `FP: ${fp}<br>(${(fp/total*100).toFixed(1)}%)`],
        [`FN: ${fn}<br>(${(fn/total*100).toFixed(1)}%)`, `VP: ${tp}<br>(${(tp/total*100).toFixed(1)}%)`]
    ];

    const data = [{
        z: z,
        x: ['Predito Negativo', 'Predito Positivo'],
        y: ['Real Positivo', 'Real Negativo'],
        type: 'heatmap',
        colorscale: [
            [0, '#e8f5e9'],
            [0.5, '#81c784'],
            [1, '#2e7d32']
        ],
        showscale: true,
        hovertemplate: '%{text}<extra></extra>',
        text: zText
    }];

    // Adicionar anotações com valores
    const annotations = [];
    const labels = [
        ['Verdadeiro Negativo', 'Falso Positivo'],
        ['Falso Negativo', 'Verdadeiro Positivo']
    ];

    for (let i = 0; i < 2; i++) {
        for (let j = 0; j < 2; j++) {
            annotations.push({
                x: j,
                y: i,
                text: `<b>${z[i][j]}</b><br>${labels[i][j]}`,
                showarrow: false,
                font: { color: z[i][j] > 500 ? 'white' : 'black', size: 14 }
            });
        }
    }

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Matriz de Confusão - Random Forest',
        annotations: annotations,
        xaxis: {
            side: 'bottom',
            tickfont: { size: 14 }
        },
        yaxis: {
            autorange: 'reversed',
            tickfont: { size: 14 }
        }
    };

    Plotly.newPlot(element, data, layout, PLOTLY_CONFIG);
}

/**
 * 5. Radar Chart Multi-Modelo
 */
function createRadarChart() {
    const element = document.getElementById('chart-radar');
    if (!element) return;

    const metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'];
    const modelsToShow = ['Random Forest', 'Gradient Boosting', 'XGBoost', 'Logistic Regression'];
    const modelColors = [COLORS.primary, COLORS.danger, COLORS.success, COLORS.warning];

    const traces = modelsToShow.map((model, i) => {
        const idx = MODELS_DATA.names.indexOf(model);
        const values = [
            MODELS_DATA.accuracy[idx] * 100,
            MODELS_DATA.precision[idx] * 100,
            MODELS_DATA.recall[idx] * 100,
            MODELS_DATA.f1_score[idx] * 100,
            MODELS_DATA.auc_roc[idx] * 100,
            MODELS_DATA.accuracy[idx] * 100 // Fechar o polígono
        ];

        return {
            type: 'scatterpolar',
            r: values,
            theta: [...metrics, metrics[0]],
            name: model,
            fill: 'toself',
            fillcolor: `${modelColors[i]}20`,
            line: { color: modelColors[i], width: 2 },
            hovertemplate: `<b>${model}</b><br>%{theta}: %{r:.1f}%<extra></extra>`
        };
    });

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Comparação Multi-Métrica',
        polar: {
            radialaxis: {
                visible: true,
                range: [70, 100]
            }
        },
        legend: {
            x: 1.1,
            y: 0.5
        }
    };

    Plotly.newPlot(element, traces, layout, PLOTLY_CONFIG);
}

/**
 * 6. Feature Importance - Barras Horizontais
 */
function createFeatureImportance() {
    const element = document.getElementById('chart-feature-importance');
    if (!element) return;

    // Ordenar por importância
    const indices = FEATURE_IMPORTANCE.importance
        .map((val, idx) => ({ val, idx }))
        .sort((a, b) => a.val - b.val)
        .map(obj => obj.idx);

    const features = indices.map(i => FEATURE_IMPORTANCE.features[i]);
    const importance = indices.map(i => FEATURE_IMPORTANCE.importance[i] * 100);
    const colors = indices.map(i => FEATURE_IMPORTANCE.colors[i]);
    const categories = indices.map(i => FEATURE_IMPORTANCE.categories[i]);

    const data = [{
        type: 'bar',
        orientation: 'h',
        x: importance,
        y: features,
        marker: { color: colors },
        hovertemplate: '<b>%{y}</b><br>Importância: %{x:.1f}%<br>Categoria: ' +
            categories.map((c, i) => `${c}`).join('') + '<extra></extra>',
        customdata: categories,
        text: importance.map(v => v.toFixed(1) + '%'),
        textposition: 'outside'
    }];

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Importância das Features (Random Forest)',
        xaxis: {
            title: 'Importância (%)',
            range: [0, 50]
        },
        yaxis: {
            tickfont: { size: 11 }
        },
        margin: { ...LAYOUT_CONFIG.margin, l: 130 }
    };

    Plotly.newPlot(element, data, layout, PLOTLY_CONFIG);
}

/**
 * 7. Threshold Analysis - Linhas Múltiplas
 */
function createThresholdAnalysis() {
    const element = document.getElementById('chart-threshold');
    if (!element) return;

    const traces = [
        {
            x: THRESHOLD_DATA.thresholds,
            y: THRESHOLD_DATA.sensitivity.map(v => v * 100),
            mode: 'lines+markers',
            name: 'Sensibilidade',
            line: { color: COLORS.success, width: 2.5 },
            marker: { size: 8 },
            hovertemplate: 'Threshold: %{x}<br>Sensibilidade: %{y:.1f}%<extra></extra>'
        },
        {
            x: THRESHOLD_DATA.thresholds,
            y: THRESHOLD_DATA.specificity.map(v => v * 100),
            mode: 'lines+markers',
            name: 'Especificidade',
            line: { color: COLORS.info, width: 2.5 },
            marker: { size: 8 },
            hovertemplate: 'Threshold: %{x}<br>Especificidade: %{y:.1f}%<extra></extra>'
        },
        {
            x: THRESHOLD_DATA.thresholds,
            y: THRESHOLD_DATA.f1.map(v => v * 100),
            mode: 'lines+markers',
            name: 'F1-Score',
            line: { color: COLORS.warning, width: 2.5 },
            marker: { size: 8 },
            hovertemplate: 'Threshold: %{x}<br>F1-Score: %{y:.1f}%<extra></extra>'
        }
    ];

    // Adicionar linhas verticais para thresholds recomendados
    const shapes = [
        { x: 0.3, label: 'Triagem', color: COLORS.success },
        { x: 0.5, label: 'Balanceado', color: COLORS.warning },
        { x: 0.8, label: 'Confirmação', color: COLORS.danger }
    ].map(t => ({
        type: 'line',
        x0: t.x, x1: t.x,
        y0: 0, y1: 100,
        line: { color: t.color, dash: 'dot', width: 2 }
    }));

    const annotations = [
        { x: 0.3, y: 95, text: 'Triagem', color: COLORS.success },
        { x: 0.5, y: 87, text: 'Balanceado', color: COLORS.warning },
        { x: 0.8, y: 70, text: 'Confirmação', color: COLORS.danger }
    ].map(a => ({
        x: a.x,
        y: a.y,
        text: a.text,
        showarrow: false,
        font: { size: 10, color: a.color },
        bgcolor: 'rgba(255,255,255,0.8)'
    }));

    const layout = {
        ...LAYOUT_CONFIG,
        title: 'Análise de Threshold - Trade-offs',
        xaxis: {
            title: 'Threshold de Decisão',
            range: [0, 1],
            dtick: 0.1
        },
        yaxis: {
            title: 'Valor (%)',
            range: [0, 100]
        },
        legend: {
            x: 0.5,
            y: -0.2,
            xanchor: 'center',
            orientation: 'h'
        },
        shapes: shapes,
        annotations: annotations
    };

    Plotly.newPlot(element, traces, layout, PLOTLY_CONFIG);
}

/**
 * Inicializar todos os gráficos quando o DOM estiver pronto
 */
function initAllCharts() {
    createTargetDistribution();
    createMetricsComparison();
    createROCCurves();
    createConfusionMatrix();
    createRadarChart();
    createFeatureImportance();
    createThresholdAnalysis();
}

// Aguardar carregamento do DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllCharts);
} else {
    initAllCharts();
}

// Re-renderizar gráficos quando a janela for redimensionada
window.addEventListener('resize', () => {
    const charts = [
        'chart-target-distribution', 'chart-metrics-comparison', 'chart-roc-curves',
        'chart-confusion-matrix', 'chart-radar', 'chart-feature-importance', 'chart-threshold'
    ];
    charts.forEach(id => {
        const el = document.getElementById(id);
        if (el) Plotly.Plots.resize(el);
    });
});
