# Pre-processamento do notebook 02_data_preprocessing_improved.ipynb

Este documento descreve, de forma didatica e objetiva, cada subsecao do notebook `02_data_preprocessing_improved.ipynb`. O foco e explicar o pipeline de pre-processamento e as validacoes aplicadas.

## 1. Setup e Importacoes

- Define caminhos do projeto e constantes globais (pastas de dados, modelos e resultados).
- Adiciona `08_src/` ao `sys.path` para permitir imports de modulos internos.
- Importa bibliotecas de dados e ML: `pandas`, `numpy`, `sklearn` e `imblearn`.
- Define `print_section()` para formatar a saida do notebook.
- Configura estilo dos graficos e informa se Plotly esta disponivel.

## 2. Carregamento de Dados

- Carrega o arquivo `Hypertension-risk-model-main.csv` a partir de caminhos conhecidos.
- Se nao encontrar o arquivo, gera erro para evitar pipeline sem dados reais.
- Traduz nomes de colunas do ingles para portugues usando um dicionario de mapeamento.
- Exibe dimensoes, distribuicao da target e total de valores ausentes.

## 3. Pre-processamento Inicial (visao rapida)

- Reforca que a EDA completa esta no notebook 01.
- Exibe novamente dimensoes, distribuicao da target e quantidade de missing values.
- Calcula razao de desbalanceamento e deixa claro que SMOTE sera aplicado apenas no treino.

## 4. Pre-processamento Inicial (imputacao)

- Separa `X` (features) e `y` (target).
- Conta valores ausentes.
- Imputa valores ausentes:
  - Numericos: mediana.
  - Categoricos: valor mais frequente.
- Garante que o dataset siga para a modelagem sem missing values.

## 5. Teste de Multiplas Proporcoes Treino/Teste

- Testa varias proporcoes treino/teste (0.15 a 0.35 de teste).
- Para cada proporcao, executa 5 validacoes com seeds diferentes.
- Em cada validacao:
  - Divide dados com `train_test_split` estratificado.
  - Aplica SMOTE somente no treino.
  - Treina RandomForest e mede `recall`, `F2` e contagem de falsos negativos.
- Consolida resultados por proporcao com media e desvio.
- Define um score combinado (F2 + estabilidade) e escolhe a melhor proporcao.
- Verifica se a diferenca para a segunda melhor proporcao e estatisticamente relevante.
- Salva resultados em `04_reports/preprocessing/teste_proporcoes_granular.csv`.

## 6. Aplicacao correta do SMOTE

- Aplica a ordem correta para evitar data leakage:
  1) Dividir treino/teste de forma estratificada.
  2) Aplicar SMOTE apenas no treino.
  3) Manter teste intocado.
- Imprime distribuicoes antes e depois, validando que:
  - A proporcao original foi mantida no teste.
  - O treino foi balanceado pelo SMOTE.
- Cria copias de referencia (`X_train_original`, `y_train_original`) para comparacoes posteriores.

## 7. Validacoes pos-SMOTE

### 7.1 Analise de outliers pos-SMOTE

- Verifica se o SMOTE introduziu valores extremos fora do padrao.
- Compara estatisticas (media, desvio, limites) entre treino original e treino sintetico.
- Armazena resultados em `04_reports/validation/post_smote_outliers_analysis.json`.

### 7.2 Preservacao de correlacoes

- Calcula matriz de correlacao nas features numericas.
- Compara correlacoes entre dados originais e balanceados.
- Aponta possiveis degradacoes e salva em `04_reports/validation/correlation_preservation_analysis.json`.

## 8. Comparacao de tecnicas de escalonamento

- Compara `StandardScaler`, `RobustScaler` e `MinMaxScaler`.
- Para cada scaler:
  - Reescala treino e teste.
  - Treina modelo e calcula F1 medio e estabilidade.
- Ordena resultados e escolhe o scaler com melhor performance e estabilidade.
- Faz recomendacao textual considerando robustez a outliers.
- Salva analise em `04_reports/validation/scaler_comparison_analysis.json`.

## 9. Escalonamento de features

- Aplica `StandardScaler` (ou o melhor scaler se ja definido) nas colunas numericas.
- Verifica medias proximas de 0 e desvios proximos de 1 para validar escalonamento.

## 10. Resumo do pipeline

- Imprime um resumo das melhorias metodologicas:
  - Eliminacao de redundancias com notebook 01.
  - Teste granular de proporcoes.
  - SMOTE aplicado corretamente.
  - Validacoes pos-SMOTE.
  - Comparacao de scalers.
- Exibe estatisticas finais do treino/teste e lista os arquivos gerados.

## 11. Salvamento dos dados processados

- Salva conjuntos em `00_data/processed`:
  - `X_train.npy`, `X_train_balanced.npy`, `X_test.npy`.
  - `y_train.npy`, `y_train_balanced.npy`, `y_test.npy`.
- Salva `metadata.json` com informacoes da proporcao escolhida e distribuicoes.
- Salva `04_reports/preprocessing/teste_proporcoes.csv`.

## 12. Validacoes finais

- Executa 8 testes de qualidade, incluindo:
  - Treino balanceado.
  - Teste preservando distribuicao original.
  - SMOTE aplicado (treino maior que original).
  - Consistencia de features e ausencia de missing values.
  - Existencia dos arquivos gerados.
  - Metricas minimas (F2 >= 0.60 e Recall >= 0.65).
- Calcula taxa de sucesso e imprime recomendacao final.

## 13. Resumo final

- Reforca ganhos do pipeline:
  - Sem data leakage.
  - Proporcao otimizada de treino/teste.
  - Validacoes automaticas e reproduciveis.
- Indica proximos passos (feature engineering e modelagem).
- Mostra como carregar os arquivos gerados no proximo notebook.
