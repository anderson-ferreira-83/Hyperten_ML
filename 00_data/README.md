# Diretorio de Dados

Este diretorio contem os dados utilizados no projeto de predicao de risco de hipertensao.

## Estrutura

```
00_data/
|-- raw/                       # Dados brutos (originais, nao modificados)
|   |-- Hypertension-risk-model-main.csv
|-- processed/                 # Dados processados (gerados pelos notebooks)
```

## Descricao dos diretorios

### raw/
Contem os dados brutos originais baixados do Kaggle. Estes dados nao devem ser modificados.

- Arquivo principal: `Hypertension-risk-model-main.csv`
- Fonte: https://www.kaggle.com/datasets/khan1803115/hypertension-risk-model-main/data
- Descricao: Dataset com 4.240 pacientes e 13 variaveis relacionadas ao risco de hipertensao

Como obter o arquivo:
1. Acesse o link acima
2. Baixe o arquivo `Hypertension-risk-model-main.csv`
3. Coloque o arquivo em `00_data/raw/`

### processed/
Contem dados processados gerados durante a execucao dos notebooks:
- Dados pre-processados (missing values tratados, escalonamento, etc.)
- Conjuntos de treino e teste
- Outros arquivos intermediarios

Nota: Estes arquivos sao gerados automaticamente e podem ser recriados executando os notebooks.

## Uso nos notebooks

Os notebooks (01 a 05) estao configurados para carregar o CSV a partir de:
1. `../00_data/raw/Hypertension-risk-model-main.csv` (quando executado em `02_notebooks/`)
2. `00_data/raw/Hypertension-risk-model-main.csv` (quando executado na raiz)

## Variaveis do dataset

| Variavel Original | Traducao PT-BR | Descricao |
|-------------------|----------------|-----------|
| male | sexo | Sexo (0: feminino, 1: masculino) |
| age | idade | Idade em anos |
| currentSmoker | fumante_atualmente | Status de fumante atual (0: nao, 1: sim) |
| cigsPerDay | cigarros_por_dia | Numero de cigarros por dia |
| BPMeds | medicamento_pressao | Uso de medicamentos para pressao (0: nao, 1: sim) |
| diabetes | diabetes | Diagnostico de diabetes (0: nao, 1: sim) |
| totChol | colesterol_total | Colesterol total em mg/dL |
| sysBP | pressao_sistolica | Pressao arterial sistolica em mmHg |
| diaBP | pressao_diastolica | Pressao arterial diastolica em mmHg |
| BMI | imc | Indice de Massa Corporal |
| heartRate | frequencia_cardiaca | Frequencia cardiaca em bpm |
| glucose | glicose | Glicose em mg/dL |
| Risk / TenYearCHD | risco_hipertensao | Variavel target (0: baixo risco, 1: alto risco) |

## Observacoes importantes

- Arquivos em `00_data/raw/` e `00_data/processed/` nao sao versionados.
- `00_data/raw/` deve conter apenas dados originais, nao modificados.
- Todos os dados processados devem ser salvos em `00_data/processed/`.
