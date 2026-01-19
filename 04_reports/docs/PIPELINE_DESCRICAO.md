# PIPELINE_DESCRICAO

Este documento descreve o pipeline completo do projeto, da analise nos notebooks ate a inferencia atual. Inclui o fluxo de dados, artefatos gerados e locais de salvamento apos a reorganizacao do repositorio.

## 1. Visao geral do fluxo

1) Ingestao de dados brutos (Kaggle)
2) EDA e validacoes iniciais
3) Pre-processamento (imputacao, escalonamento, split, SMOTE no treino)
4) Treinamento e comparacao de modelos
5) Otimizacao de hiperparametros e threshold
6) Interpretabilidade e relatorios finais
7) Empacotamento para inferencia (pipeline + features + thresholds)
8) API + UI para consumo

## 2. Notebooks (fonte das etapas)

- `02_notebooks/01_exploratory_analysis/01_exploratory_analysis_improved.ipynb`
  - EDA, estatisticas descritivas, missing values, distribuicoes, correlacoes, VIF.

- `02_notebooks/02_data_preprocessing/02_data_preprocessing_improved.ipynb`
  - Split 65/35, imputacao, escalonamento, SMOTE somente no treino.
  - Salva dados processados e metadados do pre-processamento.

- `02_notebooks/03_model_training/03_model_training_imrpoved.ipynb`
  - Treino com CV, metricas (F2, recall, FN) e resultados finais.
  - Salva modelos treinados e metricas.

- `02_notebooks/04_analysis_optimization/04_analysis_optimization_improved.ipynb`
  - Analises comparativas, grids, threshold e selecao final.
  - Gera visualizacoes e relatorios executivos.

- `02_notebooks/05_interpretability_reports/05_interpretability_reports_improved.ipynb`
  - Interpretabilidade (feature importance, SHAP, partial dependence).
  - Relatorios finais clinicos e tecnicos.

## 3. Dados e pre-processamento

### Fonte de dados
- CSV bruto: `00_data/raw/Hypertension-risk-model-main.csv`

### Pre-processamento
- Traducoes de colunas (ex.: `age -> idade`, `sysBP -> pressao_sistolica`).
- Imputacao de missing values com mediana (numericos).
- Escalonamento com StandardScaler.
- SMOTE aplicado apenas no conjunto de treino.
- Split 65/35 com `random_state=42`.

### Artefatos de dados
- `00_data/processed/X_train.npy`
- `00_data/processed/X_train_balanced.npy`
- `00_data/processed/X_test.npy`
- `00_data/processed/y_train.npy`
- `00_data/processed/y_train_balanced.npy`
- `00_data/processed/y_test.npy`
- `00_data/processed/metadata.json`

## 4. Treinamento e modelos

### Modelo oficial de inferencia
- Random Forest (selecionado por apresentar melhor Recall e F2-Score)
- Hiperparametros: `n_estimators=210`, `max_depth=24`, `min_samples_leaf=3`, `max_features='log2'`, `class_weight='balanced_subsample'`
- Metricas: Recall=92.0%, F2-Score=0.89, AUC-ROC=0.95

### Modelos treinados
- Treinados: `03_models/trained/*.pkl`
- Finais: `03_models/final/*.pkl`

### Relatorios de modelagem
- `04_reports/modeling/model_training_summary.json`
- `04_reports/modeling/model_training_report.md`
- `04_reports/modeling/final_model_results.csv`
- `04_reports/modeling/cross_validation_results.csv`

## 5. Otimizacao e visualizacoes

- Graficos e comparacoes: `04_reports/visualizations/*`
- Comparacoes de modelos: `04_reports/model_comparison/*`
- Relatorios executivos: `04_reports/executive/*`
- Analises de pre-processamento: `04_reports/preprocessing/*`
- EDA: `04_reports/eda/*`

## 6. Interpretabilidade e thresholds clinicos

- Interpretabilidade consolidada: `04_reports/interpretability/interpretability_report.json`
- Thresholds clinicos: `04_reports/interpretability/clinical_thresholds_analysis.csv`
- Feature importance: `04_reports/interpretability/feature_importance_*.csv`
- Predicoes explicadas: `04_reports/interpretability/final_predictions_with_explanations.csv`

## 7. Pipeline de inferencia (artefatos oficiais)

### Localidade
- `05_artifacts/rf_v1/`

### Conteudo
- `pipeline.pkl` (imputer + scaler + modelo)
- `imputer.pkl`
- `scaler.pkl`
- `model.pkl`
- `features.json` (ordem oficial das features)
- `thresholds.json` (screening/confirmation/balanced)
- `metadata.json`

### Ordem oficial das features
1. sexo
2. idade
3. fumante_atualmente
4. cigarros_por_dia
5. medicamento_pressao
6. diabetes
7. colesterol_total
8. pressao_sistolica
9. pressao_diastolica
10. imc
11. frequencia_cardiaca
12. glicose

### Observacoes
- SMOTE NAO e usado na inferencia.
- Thresholds clinicos foram consolidados a partir do CSV em `04_reports/interpretability/clinical_thresholds_analysis.csv`.
- Perfil `balanced` e `screening` usam threshold 0.3 (maior F1/recall no conjunto analisado).

## 8. API e UI

### API (FastAPI)
- Arquivo: `06_api/main.py`
- Endpoints:
  - `GET /health`
  - `GET /app` (UI)
  - `POST /predict?threshold_key=balanced`

### UI (HTML/CSS/JS)
- `07_web/index.html`
- `07_web/styles.css`, `07_web/styles.min.css`
- `07_web/app.js`, `07_web/app.min.js`

### Inferencia local
- Script: `08_src/inference/inference.py`
- Tutorial: `04_reports/docs/TUTORIAL_INFERENCIA_LOCAL.md`

## 9. Estrutura organizada (pos-reorganizacao)

- `05_artifacts/` pipelines e metadados de inferencia
- `06_api/` backend FastAPI
- `07_web/` interface HTML/CSS/JS
- `00_data/` dados brutos e processados
- `03_models/` modelos treinados/finais
- `04_reports/` relatorios e visualizacoes
- `99_legacy/` arquivos historicos (ex.: `99_legacy/legacy`)

## 10. Peculiaridades e decisoes importantes

- Modelo oficial: Random Forest (melhor Recall=92% e F2=0.89, conforme analise comparativa).
- Pipeline de inferencia consolidado em `05_artifacts/rf_v1`.
- Dados processados foram movidos de `02_notebooks/data/processed` para `00_data/processed`.
- Relatorios foram consolidados em `04_reports/` e podem exigir ajustes em notebooks antigos que escreviam em `02_notebooks/results`.
