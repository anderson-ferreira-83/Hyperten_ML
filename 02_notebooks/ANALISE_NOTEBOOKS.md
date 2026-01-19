# Analise individual dos notebooks (pasta notebooks)

Este documento resume e analisa, de forma individual, cada notebook da pasta `notebooks`, e verifica a consistencia do fluxo para uso em TCC.

## 01_exploratory_analysis_improved.ipynb

**Objetivo**
- EDA completa do dataset de hipertensao, com foco em qualidade de dados, distribuicoes, outliers, correlacoes e sinais estatisticos para guiar o pre-processamento.

**Fluxo principal**
- Carregamento do dataset (varios caminhos; se nao encontrado, cria dados sinteticos para demonstracao).
- Traducao e padronizacao dos nomes das colunas.
- Analises de nulos, variavel target, distribuicoes numericas, outliers, correlacoes e VIF.
- Analise estatistica comparativa (effect size e significancia).
- Resumo executivo e recomendacoes para o pre-processamento.

**Entradas/saidas**
- Entradas: `../00_data/raw/Hypertension-risk-model-main.csv`, `00_data/raw/Hypertension-risk-model-main.csv`, `hypertension_data.csv`.
- Saidas: figuras e relatorios visuais (salvos via `save_figure`, quando aplicado).

**Pontos fortes**
- EDA profunda e estruturada, com explicacao clara e resumo executivo.
- Avalia multicolinearidade (VIF) e sugere acoes.
- Inclui testes estatisticos e efeito para apoiar selecao de variaveis.

**Atencoes / consistencia**
- Fallback para dados sinteticos: se o arquivo real nao existir, os resultados deixam de ser reprodutiveis para o TCC. Para publicacao, garanta que o dataset real esta presente e registre a origem.
- Padronizacao de nomes: essencial manter o mesmo mapeamento nas etapas seguintes para evitar inconsistencias de features.

## 02_data_preprocessing_improved.ipynb

**Objetivo**
- Preparar dados para modelagem com pipeline robusto: split estratificado, SMOTE apenas no treino, comparacao de proporcoes treino/teste, escalonamento e validacoes.

**Fluxo principal**
- Carregamento do dataset.
- Pre-processamento inicial.
- Teste de multiplas proporcoes treino/teste com repeticoes para reduzir variancia.
- Aplicacao correta de SMOTE (apenas no treino) e validacoes anti data leakage.
- Comparacao de escalonadores (Standard, MinMax, Robust).
- Validacao de preservacao de correlacoes e outliers pos-SMOTE.
- Salvamento de arrays e metadados processados.

**Entradas/saidas**
- Entradas: `00_data/raw/Hypertension-risk-model-main.csv` (e caminhos alternativos).
- Saidas principais: `00_data/processed/X_train.npy`, `00_data/processed/X_test.npy`, `00_data/processed/y_train.npy`, `00_data/processed/y_test.npy`, `00_data/processed/X_train_balanced.npy`, `00_data/processed/y_train_balanced.npy`, `00_data/processed/metadata.json`.
- Relatorios de validacao: `04_reports/validation/*.json`, `04_reports/preprocessing/teste_proporcoes*.csv`.

**Pontos fortes**
- Preocupacao explicita com data leakage (SMOTE aplicado apenas no treino).
- Comparacao sistematica de proporcoes e escalonadores, com salvamento de resultados.
- Validacoes adicionais de consistencia (correlacao, outliers pos-SMOTE).

**Atencoes / consistencia**
- Existem varios caminhos de arquivo e nomes duplicados (em raiz e em `00_data/processed`). Definir um caminho canonico no TCC evita confusao.
- Se o notebook for executado com parametros/seed diferentes, os splits e resultados mudam. Para TCC, fixe e documente o `random_state`.

## 03_model_training_imrpoved.ipynb

**Objetivo**
- Treinar e comparar modelos, com validacao cruzada e salvamento de resultados.

**Fluxo principal**
- Carregamento dos dados processados (incluindo treino balanceado).
- Definicao de metricas (F1, F2, ROC AUC, precision, recall) e validacao cruzada estratificada.
- Treinamento de varios modelos (ex.: Logistic Regression, Random Forest, Gradient Boosting, XGBoost, etc.).
- Comparacao e salvamento de resultados, incluindo metadados e modelos treinados.

**Entradas/saidas**
- Entradas: `00_data/processed/X_train_balanced.npy`, `00_data/processed/X_test.npy`, `00_data/processed/y_train_balanced.npy`, `00_data/processed/y_test.npy`, `00_data/processed/metadata.json`.
- Saidas: `04_reports/model_comparison/model_results.csv`, `03_models/trained/all_trained_models.pkl`, `03_models/trained/best_model.pkl`, `02_notebooks/06_model_metrics/6_analysis_metrics/cross_validation_results.csv`, `02_notebooks/06_model_metrics/6_analysis_metrics/final_model_results.csv`.

**Pontos fortes**
- Pipeline com validacao cruzada estratificada e metricas alinhadas ao problema.
- Registro de resultados e modelos para reproducao.

**Atencoes / consistencia**
- A validacao cruzada e feita sobre o conjunto ja balanceado com SMOTE. Isso pode superestimar desempenho em alguns cenarios. No notebook 04 ha uma abordagem corrigida (SMOTE no pipeline durante CV). Para consistencia metodologica, use a estrategia do notebook 04 como referencia principal.
- O nome do arquivo e "imrpoved" (typo). Para publicacao, considere padronizar nomes.

## 04_analysis_optimization_improved.ipynb

**Objetivo**
- Analise detalhada de performance e otimizacao de hiperparametros com abordagem corrigida para evitar data leakage.

**Fluxo principal**
- Carregamento de dados e modelos.
- Retreinamento para analises comparativas (curvas ROC, PR, importancia de features).
- Analise de erros.
- Otimizacao por GridSearch e RandomizedSearch.
- Uso de pipeline com SMOTE dentro da validacao cruzada (correcao para leakage).

**Entradas/saidas**
- Entradas: `00_data/processed/X_train.npy`, `00_data/processed/y_train.npy`, `03_models/trained/best_model.pkl`, `04_reports/model_comparison/model_results.csv` (e variantes).
- Saidas: `03_models/final/*_optimized.pkl`, `04_reports/executive/*`, `04_reports/model_comparison/model_results.csv`.

**Pontos fortes**
- Corrige o problema de SMOTE dentro da validacao cruzada (mais rigoroso).
- Relatorios visuais e analise de erros enriquecem o diagnostico.
- Otimizacao sistematica de hiperparametros.

**Atencoes / consistencia**
- Mistura de caminhos para modelos (ex.: `03_models/trained/best_model.pkl` vs `models/best_model.pkl`). Definir um caminho unico reduz risco de inconsistencia.
- O notebook espera dados originais (nao balanceados) para GridSearch com pipeline. Isso deve estar alinhado ao notebook 02.

## 05_interpretability_reports_improved.ipynb

**Objetivo**
- Interpretabilidade e relatorios finais, incluindo SHAP, partial dependence e analise clinica.

**Fluxo principal**
- Carregamento do melhor modelo e dados processados.
- Analise de interpretabilidade com feature importance, SHAP (se disponivel) e partial dependence.
- Visualizacoes e interpretacao clinica.
- Gera arquivos finais de relatorio e exportacoes.

**Entradas/saidas**
- Entradas: `04_reports/00_data/processed_data_full.csv` (ou equivalente), `feature_scaler.pkl`, modelos individuais (`Random_Forest.pkl`, `Gradient_Boosting.pkl`, `Logistic_Regression.pkl`).
- Saidas: `interpretability_report.json`, `model_interpretability_analysis.png`, `final_predictions_with_explanations.csv`, `clinical_*_analysis.csv`.

**Pontos fortes**
- Foco claro em interpretabilidade e traducao para contexto clinico.
- Uso condicional de SHAP com fallback quando nao disponivel.

**Atencoes / consistencia**
- O notebook faz `train_test_split` novamente. Para TCC, o ideal e reutilizar o mesmo split/indices do treinamento para garantir consistencia entre performance e interpretabilidade.
- Os nomes dos arquivos de modelo nao parecem os mesmos gerados no notebook 03. Ajustar para evitar carregamento incorreto.
- Garantir que as features e o scaler estejam na mesma ordem usada no treino; caso contrario, as explicacoes podem ficar inconsistentes.

## Verificacao de consistencia e ordem do fluxo

**Ordem esperada (coerente)**
1. `01_exploratory_analysis_improved.ipynb` (EDA)
2. `02_data_preprocessing_improved.ipynb` (pre-processamento)
3. `03_model_training_imrpoved.ipynb` (treinamento e comparacao)
4. `04_analysis_optimization_improved.ipynb` (analise e otimizacao)
5. `05_interpretability_reports_improved.ipynb` (interpretabilidade)

**Consistencias observadas**
- O fluxo macro esta correto e progressivo.
- Ha preocupacao explicita com data leakage e validacao cruzada estratificada.
- Salvamento de artefatos (dados processados, modelos e relatorios) permite reproducao.

**Inconsistencias que merecem ajuste**
- Dataset real vs sintetico no notebook 01: para TCC, evitar o uso de dados sinteticos ou separar em apendice/metodologia.
- Caminhos de arquivos duplicados e nomes distintos (ex.: `03_models/trained/best_model.pkl` vs `models/best_model.pkl`, `processed_data_full.csv` vs `00_data/processed/*.npy`). Padronizar um caminho oficial.
- Metodologia de CV: notebook 03 usa treino ja balanceado; notebook 04 corrige com pipeline de SMOTE dentro de CV. Para consistencia, priorizar a metodologia do notebook 04 e alinhar o notebook 03.
- Re-split no notebook 05: ideal reaproveitar o mesmo split para interpretabilidade, evitando divergencias.

## Resumo final (pontos fortes e fragilidades)

**Pontos fortes**
- EDA robusta, com analise estatistica, VIF e resumo executivo.
- Pre-processamento cuidadoso com validacoes de leakage e comparacoes de escalonamento.
- Pipeline de modelagem abrangente e com otimizacao de hiperparametros.
- Interpretabilidade com SHAP/PDP e alinhamento clinico.

**Fragilidades / ajustes recomendados**
- Padronizar caminhos e nomes de arquivos para dados e modelos.
- Fixar e documentar seeds e splits em todas as etapas.
- Alinhar a validacao cruzada ao metodo correto (SMOTE no pipeline de CV).
- Evitar gerar dados sinteticos como base de resultados principais.
- Evitar novo split no notebook de interpretabilidade; usar o mesmo conjunto do treinamento.

**Possiveis adicoes**
- Uma tabela final consolidada com metricas (media e desvio padrao) para todos os modelos.
- Um diagrama simples do pipeline (EDA -> preprocess -> treino -> otimizacao -> interpretabilidade).
- Uma secao curta de limitacoes (ex.: dependencia de dataset publico e validade externa).

**Possiveis remocoes**
- Mensagens de log muito repetitivas, se o material for usado em texto do TCC (manter apenas as mais explicativas).

Conclusao: o fluxo esta bem estruturado e pronto para TCC, desde que os pontos de consistencia acima sejam ajustados e documentados.
