# Reestruturacao completa (Capitulo 2 ate Conclusao) — formato ABNT, didatica reforcada e mapeamento direto

Este documento substitui a versao anterior, reestrutura os capitulos 2 a conclusao em formato ABNT (numeracao hierarquica), explica termos tecnicos (ex.: CV, XAI, fallback) e mapeia cada bloco de texto aos notebooks e aos HTMLs. O objetivo e permitir a escrita direta do texto final do TCC, com consistencia metodologica, narrativa e didatica clara.

## 0. Glossario didatico (termos que aparecem no texto)

**CV (Cross-Validation / Validacao Cruzada)**  
Tecnica de avaliacao em que o conjunto de treino e dividido em K partes (folds). O modelo e treinado em K-1 partes e avaliado na parte restante, repetindo ate usar todas as partes. Gera uma media de desempenho mais confiavel do que uma unica divisao treino/teste.

**Stratified K-Fold (CV estratificada)**  
Variante da CV que preserva a proporcao das classes em cada fold. E essencial em datasets desbalanceados (como saude), pois evita folds com distribuicao distorcida.

**SMOTE**  
Tecnica de balanceamento que cria amostras sinteticas da classe minoritaria por interpolacao entre vizinhos. Evita duplicacao simples e reduz overfitting.

**Pipeline**  
Encadeamento de etapas (ex.: SMOTE -> escalonamento -> modelo) aplicado de forma consistente. Em CV, o pipeline garante que cada fold receba o mesmo tratamento sem vazamento de dados.

**Data leakage (vazamento de dados)**  
Quando informacoes do conjunto de teste vazam para o treino, inflando as metricas. Exemplo: aplicar SMOTE antes de dividir os dados. A solucao correta e aplicar SMOTE apenas no treino e, em CV, dentro do pipeline.

**Fallback**  
Estrategia alternativa usada quando a principal falha (ex.: dataset nao encontrado). No TCC, o fallback deve ser evitado nos resultados finais para garantir reprodutibilidade.

**XAI (Explainable AI)**  
Conjunto de tecnicas que explicam as decisoes do modelo. Em saude, a interpretabilidade e obrigatoria para confianca clinica.

**SHAP**  
Metodo de XAI que estima a contribuicao de cada feature para a previsao. Gera explicacoes globais e locais.

**PDP (Partial Dependence Plot)**  
Grafico que mostra o efeito medio de uma feature na previsao, mantendo outras variaveis constantes.

## 1. Diagnostico do PDF (pontos observados)

Pelo sumario e trechos extraidos do PDF, a estrutura atual cobre:
- Cap. 2: Referencial teorico (hipertensao, ML, metricas, validacao, algoritmos, XAI).
- Cap. 3: Metodologia (base de dados, pre-processamento, validacao, modelagem, metricas).
- Cap. 4: Resultados e discussao (proporcoes treino/teste, comparacao de modelos, CV, otimizacao, interpretabilidade).
- Conclusao.

O PDF ja explica metricas e conceitos, mas precisa alinhar o **texto dos resultados e a metodologia** ao **pipeline real** nos notebooks, principalmente:
- SMOTE aplicado **somente no treino** e, na CV, **dentro do pipeline**.
- Comparacao de proporcoes treino/teste com repeticoes (estabilidade).
- Valorizacao da metrica **F2** e do **Recall** devido ao custo clinico dos FNs.
- Interpretabilidade (SHAP/PDP) consistente com os dados e split do treino.

## 2. Analise minuciosa dos 5 notebooks (o que foi feito)

### 2.1 `01_exploratory_analysis_improved.ipynb` (EDA)
**Escopo real:**
- Carrega o dataset (varios caminhos). Se nao encontra, cria dados sinteticos para demonstracao.
- Traduz e padroniza nomes de colunas (chave para consistencia nos capitulos seguintes).
- Analisa nulos, distribuicoes numericas/categoricas, outliers e correlacoes.
- Calcula VIF (multicolinearidade).
- Executa analise estatistica comparativa (effect size + p-values).
- Fecha com resumo executivo e recomendacoes para pre-processamento.

**Para o texto do Cap. 2/3:**
- No referencial, usar a EDA para justificar a necessidade de balanceamento e escolha de metricas.
- Na metodologia, detalhar a traducao/padronizacao de variaveis como etapa inicial.

**Atencao para consistencia:**
- A existencia de fallback com dados sinteticos precisa ser explicitamente evitada no texto final do TCC (usar apenas o dataset real).

### 2.2 `02_data_preprocessing_improved.ipynb` (pre-processamento)
**Escopo real:**
- Divisao estratificada treino/teste (com `random_state`).
- SMOTE aplicado **apenas no treino**.
- Teste de multiplas proporcoes treino/teste com repeticoes para reduzir variancia.
- Comparacao de escalonadores (Standard/MinMax/Robust).
- Validacoes pos-SMOTE: preservacao de correlacoes e outliers.
- Salvamento de arrays `*.npy` e metadados.

**Para o texto do Cap. 3:**
- Descrever o fluxo: split -> SMOTE -> escalonamento -> validacoes.
- Justificar a escolha de proporcao treino/teste com base em estabilidade.
- Explicar porque SMOTE e preferivel a RandomOverSampler (base no tutorial do orientador).

**Atencao para consistencia:**
- Ha multiplos caminhos de arquivo. No texto, definir um caminho canonico.
- Fixar `random_state` e documentar.

### 2.3 `03_model_training_imrpoved.ipynb` (treino e comparacao)
**Escopo real:**
- Carrega dados processados (inclui treino balanceado).
- Define metricas (F1, F2, Recall, Precision, ROC AUC) e CV estratificada.
- Treina diversos modelos (Logistic Regression, Random Forest, Gradient Boosting, XGBoost, etc.).
- Salva resultados e modelos.

**Para o texto do Cap. 4:**
- Comparar modelos usando F2 como metrica principal.
- Mostrar rankings e justificar o modelo final.

**Atencao para consistencia:**
- Este notebook usa treino ja balanceado para CV. Para maior rigor, o procedimento correto e o do Notebook 04 (SMOTE dentro do pipeline durante CV). Essa diferenca deve ser ajustada no texto ou explicitada como evolucao metodologica.

### 2.4 `04_analysis_optimization_improved.ipynb` (analise e otimizacao)
**Escopo real:**
- Retreinamento para analises visuais (ROC/PR) e diagnostico de erros.
- Otimizacao com GridSearch/RandomizedSearch.
- Implementa pipeline com SMOTE dentro da CV (corrige data leakage).
- Salva modelos otimizados e relatorios executivos.

**Para o texto do Cap. 4:**
- Esta e a referencia principal de rigor metodologico.
- Descrever por que SMOTE deve estar **dentro** do pipeline de CV.
- Apresentar ganhos de performance com otimizacao e justificar modelo final.

### 2.5 `05_interpretability_reports_improved.ipynb` (interpretabilidade)
**Escopo real:**
- Carrega modelo e dados processados.
- Aplica feature importance, SHAP (se disponivel) e partial dependence.
- Produz relatorios de interpretabilidade e analise clinica.

**Para o texto do Cap. 4/Conclusao:**
- Interpretabilidade deve reforcar a validade clinica dos fatores de risco.

**Atencao para consistencia:**
- Evitar `train_test_split` novo. Para o TCC, manter o mesmo split do treinamento.
- Padronizar quais modelos finais serao explicados (mesmo nome e caminho).

## 3. O que os HTMLs adicionam (e como incorporar)

### 3.1 `guia_metricas_hipertensao.html`
**Contribuicoes chave:**
- Justifica a prioridade do Recall e F2 por causa do custo clinico dos falsos negativos.
- Explica matriz de confusao em termos clinicos (impacto real de FP vs FN).

**Como usar no Cap. 2:**
- Inserir uma subsecao explicando por que F2 e mais apropriada do que acuracia.
- Explicitar que o objetivo clinico e reduzir FN, mesmo com leve aumento de FP.

### 3.2 `tutorial_tecnicas_avancadas_orientador_bw.html`
**Contribuicoes chave:**
- Orienta a sequencia metodologica: SMOTE -> proporcoes treino/teste -> K-Fold -> Stratified K-Fold -> pipeline final.
- Justifica por que RandomOverSampler e inferior a SMOTE.
- Reforca reprodutibilidade e documentacao.

**Como usar no Cap. 3:**
- Alinhar a metodologia com essa sequencia.
- Apresentar a evolucao metodologica e o ganho esperado de rigor.

## 4. Estrutura ABNT proposta (Capitulo 2 ate Conclusao) com instrucoes de implementacao

### 4.1 Capitulo 2 — Referencial Teorico (proposta ABNT)
**Objetivo:** fundamentar clinica e tecnicamente as escolhas do pipeline.

**2.1 Hipertensao arterial: contexto clinico e epidemiologico**  
- Basear no PDF atual e reforcar a necessidade de deteccao precoce.  
- Conectar com o impacto clinico de falsos negativos (base: `guia_metricas_hipertensao.html`).

**2.2 Ciencia de dados e classificacao binaria**  
- Definir o problema de risco de hipertensao como classificacao binaria.  
- Introduzir brevemente o fluxo CRISP-DM ou pipeline de ML usado.

**2.3 Metricas de avaliacao e implicacoes clinicas**  
- Matriz de confusao com interpretacao clinica (FP vs FN).  
- Prioridade de Recall/Sensibilidade.  
- F2-Score como metrica principal (justificativa clinica).  
- Fechar com AUC-ROC e Precision como metricas complementares.

**2.4 Validacao de modelos**  
- Explicar o que e CV e por que usar K-Fold.  
- Explicar por que Stratified K-Fold e necessario em dados desbalanceados.  
- Justificar k=5 com base em equilibrio entre estabilidade e custo computacional.  
- Vincular diretamente ao que foi aplicado nos notebooks (03 e 04).

**2.5 Balanceamento de classes**  
- Limites do RandomOverSampler (overfitting e duplicacao).  
- Vantagens do SMOTE (interpolacao, melhor generalizacao).

**2.6 Interpretabilidade (XAI)**  
- Definir XAI e sua necessidade em saude.  
- Explicar o que e SHAP e o que e PDP.  
- Relacionar com as analises do notebook 05.

### 4.2 Capitulo 3 — Metodologia (proposta ABNT)
**Objetivo:** descrever o pipeline real, etapa a etapa, com reprodutibilidade.

**3.1 Base de dados e dicionario de variaveis**  
- Origem Kaggle e caracterizacao (n amostras, n features, target).  
- Tabela do dicionario (do PDF atual), alinhada aos nomes traduzidos.

**3.2 Padronizacao e traducao de variaveis**  
- Descrever o mapeamento de colunas (Notebook 01).  
- Justificar importancia para interpretabilidade.

**3.3 Tratamento de valores ausentes**  
- Descrever estrategia (mediana para continuas, conforme notebook).  
- Justificar clinicamente.

**3.4 Analise exploratoria de dados (EDA)**  
- Definir EDA (o que e e por que e feita).  
- Distribuicoes, outliers, correlacoes, VIF, effect size.  
- Indicar quais achados guiaram o pre-processamento.

**3.5 Divisao treino/teste e balanceamento**  
- Split estratificado com `random_state`.  
- SMOTE apenas no treino.  
- Justificativa baseada no tutorial do orientador.

**3.6 Teste de proporcoes treino/teste**  
- Descrever teste de proporcoes com repeticoes.  
- Definir criterio de escolha.

**3.7 Escalonamento e validacoes pos-SMOTE**  
- Comparacao de escalonadores.  
- Preservacao de correlacoes e analise de outliers pos-SMOTE.

**3.8 Validacao cruzada estratificada com pipeline**  
- Explicar o pipeline (SMOTE -> modelo) e por que ele deve estar dentro da CV.  
- Deixar claro o fluxo: em cada fold, o SMOTE e aplicado apenas no treino.  
- Justificar como prevencao de leakage (com exemplo simples).

### 4.3 Capitulo 4 — Resultados e Discussao (proposta ABNT)
**Objetivo:** apresentar resultados de forma sequencial e interpretavel.

**4.1 Resultados da EDA**  
- Distribuicao do target e grau de desbalanceamento.  
- Variaveis mais discriminantes (effect size).  
- Multicolinearidade e impacto.

**4.2 Resultados do pre-processamento**  
- Proporcoes treino/teste e criterio final.  
- Comparacao de escalonadores.  
- Validacoes pos-SMOTE.

**4.3 Comparacao de modelos**  
- Explicar que a comparacao usa CV para estabilidade.  
- Tabela de metricas (F2, Recall, Precision, ROC AUC).  
- Ranking dos modelos por F2.  
- Selecionar top-3 e justificar clinicamente.

**4.4 Validacao cruzada e escolha do modelo final**  
- Reforcar o que e CV e por que a media e mais confiavel.  
- CV estratificada com pipeline SMOTE.  
- Justificar o modelo final pelo equilibrio clinico (alto Recall + F2).

**4.5 Otimizacao de hiperparametros**  
- GridSearch/RandomizedSearch.  
- Ganhos antes/depois.

**4.6 Interpretabilidade e analise clinica**  
- Explicar o que cada tecnica mostra (feature importance, SHAP, PDP).  
- Mostrar como cada uma responde a perguntas clinicas.  
- Discutir os principais fatores identificados.

### 4.4 Capitulo 5 (se existir) — Discussao integrada
- Comparacao com literatura.  
- Trade-offs (Recall vs Precision).  
- Impacto clinico dos falsos negativos.

### 4.5 Conclusao
- Sintese do pipeline completo.  
- Ganhos com metodologias avancadas.  
- Limitacoes e trabalhos futuros.

## 5. Mapeamento direto: de onde vem cada bloco do texto (notebooks e PDF)

**Cap. 2 (Referencial teorico)**  
- Metricas e custos clinicos: `02_notebooks/guia_metricas_hipertensao.html`.  
- Tecnicas avancadas (SMOTE, K-Fold, Stratified K-Fold): `02_notebooks/tutorial_tecnicas_avancadas_orientador_bw.html`.  
- Validacao e XAI: `02_notebooks/05_interpretability_reports/05_interpretability_reports_improved.ipynb` + PDF atual.

**Cap. 3 (Metodologia)**  
- Padronizacao/EDA: `02_notebooks/01_exploratory_analysis/01_exploratory_analysis_improved.ipynb`.  
- Pre-processamento, split, SMOTE, escalonamento: `02_notebooks/02_data_preprocessing/02_data_preprocessing_improved.ipynb`.  
- Protocolo de CV com pipeline: `02_notebooks/04_analysis_optimization/04_analysis_optimization_improved.ipynb`.

**Cap. 4 (Resultados)**  
- Resultados EDA: `02_notebooks/01_exploratory_analysis/01_exploratory_analysis_improved.ipynb`.  
- Resultados pre-processamento: `02_notebooks/02_data_preprocessing/02_data_preprocessing_improved.ipynb`.  
- Comparacao de modelos: `02_notebooks/03_model_training/03_model_training_imrpoved.ipynb`.  
- Otimizacao/analise detalhada: `02_notebooks/04_analysis_optimization/04_analysis_optimization_improved.ipynb`.  
- Interpretabilidade: `02_notebooks/05_interpretability_reports/05_interpretability_reports_improved.ipynb`.

**Conclusao**  
- Sintese final: combinar resultados dos notebooks 03, 04 e 05.


## 5.1 Onde encaixar o conteudo dos HTMLs no texto (capitulos e secoes)

### 5.1.1 guia_metricas_hipertensao.html
- **Capitulo 2, secao 2.3 (Metricas de avaliacao e implicacoes clinicas)**  
  Incluir a explicacao didatica da matriz de confusao com foco clinico (FP vs FN) e a justificativa do uso de Recall e F2 como metricas principais.
- **Capitulo 4, secao 4.3 (Comparacao de modelos)**  
  Reforcar que a escolha do modelo privilegia F2 e Recall por causa do custo clinico de falsos negativos.
- **Capitulo 5/Conclusao**  
  Retomar o impacto clinico dos erros (principalmente FN) como argumento de responsabilidade metodologica.

**Exemplos de paragrafo (prontos para uso):**

Cap. 2.3  
\"Em problemas clinicos, os erros nao possuem o mesmo custo. Na matriz de confusao, falsos negativos (FN) indicam pacientes de risco classificados como sem risco, o que pode atrasar intervencoes preventivas. Por isso, privilegia-se o Recall e o F2-Score, que penalizam mais os FN e refletem melhor a necessidade clinica de identificar o maior numero possivel de pacientes em risco.\"

Cap. 4.3  
\"A comparacao entre modelos considera principalmente o F2-Score e o Recall, pois a prioridade clinica e reduzir falsos negativos. Mesmo que um modelo com maior Precisao reduza falsos positivos, um Recall baixo seria inadequado para o contexto preventivo. Assim, o ranking final e orientado pelas metricas que favorecem a sensibilidade diagnostica.\"

Conclusao  
\"O criterio de selecao do modelo privilegia a identificacao de pacientes em risco, reduzindo falsos negativos. Essa decisao metodologica reforca a responsabilidade clinica do sistema preditivo e alinha o desempenho tecnico ao impacto em saude publica.\"

### 5.1.2 tutorial_tecnicas_avancadas_orientador_bw.html
- **Capitulo 3, secao 3.5 (Divisao treino/teste e balanceamento)**  
  Explicar por que SMOTE substitui o RandomOverSampler, destacando menor overfitting.
- **Capitulo 3, secao 3.6 (Teste de proporcoes treino/teste)**  
  Inserir a justificativa da avaliacao de multiplas proporcoes (60/40, 70/30, 75/25, 80/20) e criterio de escolha.
- **Capitulo 3, secao 3.8 (Validacao cruzada estratificada com pipeline)**  
  Inserir a sequencia didatica do tutorial: SMOTE -> proporcoes -> K-Fold -> Stratified K-Fold -> pipeline final.
- **Capitulo 4, secao 4.4 (Validacao cruzada e escolha do modelo final)**  
  Explicar que a CV estratificada reduz variancia e aumenta confiabilidade dos resultados.

**Exemplos de paragrafo (prontos para uso):**

Cap. 3.5  
\"Para lidar com o desbalanceamento, utilizamos SMOTE em vez de RandomOverSampler. Enquanto a duplicacao simples pode induzir overfitting, o SMOTE cria amostras sinteticas por interpolacao, ampliando a representatividade da classe minoritaria e favorecendo melhor generalizacao.\"

Cap. 3.6  
\"Testamos diferentes proporcoes treino/teste (60/40, 70/30, 75/25 e 80/20) para identificar o equilibrio mais estavel entre variancia e capacidade preditiva. A proporcao final foi escolhida com base na consistencia das metricas em repeticoes sucessivas.\"

Cap. 3.8  
\"A validacao cruzada foi estruturada em pipeline: primeiro aplica-se SMOTE apenas no conjunto de treino de cada fold, e em seguida o modelo e ajustado. Essa sequencia (SMOTE -> K-Fold -> Stratified K-Fold) evita vazamento de dados e garante avaliacao mais realista.\"

Cap. 4.4  
\"A CV estratificada foi adotada por fornecer uma media de desempenho mais robusta e reduzir a variancia dos resultados. Ao manter a distribuicao das classes em cada fold, as metricas tornam-se comparaveis e confiaveis para selecao do modelo final.\"


## 6. Ajustes imprescindiveis para consistencia entre notebooks e PDF

1. **SMOTE e CV**: deixar explicito que SMOTE ocorre apenas no treino e, na CV, dentro do pipeline.
2. **Split unico e replicavel**: evitar novo split no notebook 05 (usar o mesmo do treino).
3. **Padronizacao de arquivos**: fixar caminhos unicos para dados e modelos.
4. **Resultados consolidados**: criar tabela final unica com medias e desvios da CV.
5. **Coerencia de nomenclaturas**: alinhar variaveis traduzidas ao longo do texto.

## 7. Checklist final para escrita

- [ ] Cap. 2 inclui justificativa clinica da metrica F2 (guia de metricas).
- [ ] Cap. 3 segue sequencia do tutorial (SMOTE -> proporcoes -> K-Fold -> Stratified K-Fold).
- [ ] Cap. 4 usa resultados consolidados e detalha pipeline correto.
- [ ] Interpretabilidade alinhada ao mesmo split do treino.
- [ ] Conclusao traz limitacoes e futuras melhorias.

## 8. Resumo final
A nova estrutura deve refletir fielmente o que foi implementado nos notebooks. O capitulo 2 deve usar o guia de metricas para reforcar a escolha da F2 e do Recall. O capitulo 3 precisa descrever o pipeline completo, na ordem didatica indicada pelo orientador. O capitulo 4 deve apresentar resultados com consistencia metodologica (especialmente sobre SMOTE e CV). A conclusao deve sintetizar ganhos, limitacoes e proximos passos.
