# Figuras Individuais para Monografia LaTeX

## Resumo das Modificações

O notebook `04_analysis_optimization_improved.ipynb` foi modificado para gerar **figuras individuais de alta qualidade** além das figuras compostas originais, otimizadas para uso em monografias LaTeX.

## Estatísticas

- **Total de células modificadas:** 9
- **Total de figuras individuais:** ~31+ (incluindo variações por modelo)
- **Formatos gerados:** PNG, SVG e PDF
- **Qualidade:** Alta resolução, otimizada para impressão e visualização digital

## Células Modificadas

| # | Célula | Tipo de Figura | Figuras Individuais |
|---|--------|----------------|---------------------|
| 1 | 10 | Model Comparison Overview | 4 |
| 2 | 12 | Confusion Matrices | N (por modelo) |
| 3 | 14 | ROC Curves | 3 |
| 4 | 16 | Precision-Recall Curves | 3 |
| 5 | 18 | Feature Importance Individual | N (por modelo) |
| 6 | 19 | Feature Importance Consensus | 4 |
| 7 | 22 | Error Probability Analysis | 4 |
| 8 | 23 | Threshold Optimization | 7 |
| 9 | 35 | Base vs Optimized Comparison | 6 |

## Como Usar

### Habilitar/Desabilitar Geração de Figuras Individuais

Cada célula modificada possui uma flag no início:

```python
# Configuração: gerar figuras individuais
GENERATE_INDIVIDUAL_FIGURES = True  # Altere para False para desabilitar
```

- **`True`**: Gera figuras compostas + figuras individuais (recomendado para monografia)
- **`False`**: Gera apenas figuras compostas (para visualização rápida)

### Executar o Notebook

Basta executar o notebook normalmente. As figuras individuais serão salvas automaticamente em:

```
notebooks/results/visualizations/
```

## Nomenclatura dos Arquivos

### Padrão de Nomenclatura

```
{numero}_{nome}_part{XX}_{descrição}.{formato}
```

### Exemplos

```
01_model_comparison_part01_metricas_performance.png
01_model_comparison_part01_metricas_performance.svg
01_model_comparison_part01_metricas_performance.pdf

03_roc_curves_part01_curvas_roc.png
03_roc_curves_part02_roc_zoom.png
03_roc_curves_part03_ranking_auc.png

08_threshold_optimization_part01_metricas.png
08_threshold_optimization_part02_erros.png
...
08_threshold_optimization_part07_impacto.png
```

## Tamanhos Otimizados

As figuras são geradas com tamanhos otimizados baseados no tipo:

| Tipo de Gráfico | Tamanho (polegadas) | Uso Ideal |
|-----------------|---------------------|-----------|
| Padrão | 12 x 8 | Gráficos de linha, barras |
| Matriz/Heatmap | 12 x 10 | Matrices de confusão, heatmaps |
| Tabela | 14 x 8 | Tabelas de dados |
| Radar | 10 x 10 | Gráficos radar |

## Características das Figuras

### Qualidade

- ✅ **Alta resolução** (DPI otimizado para impressão)
- ✅ **Vetorial** (SVG e PDF para redimensionamento sem perda)
- ✅ **Raster** (PNG para visualização rápida)

### Layout

- ✅ **Constrained layout** para melhor organização
- ✅ **Títulos descritivos** apropriados para monografia
- ✅ **Legendas preservadas** do subplot original
- ✅ **Grades e anotações** mantidas

### Conteúdo

- ✅ **Copia fiel** do subplot original
- ✅ **Escalas e limites** preservados
- ✅ **Cores e estilos** mantidos
- ✅ **Textos e anotações** transferidos

## Uso no LaTeX

### Exemplo Básico

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras/01_model_comparison_part01_metricas_performance.pdf}
    \caption{Comparação de métricas de performance entre os modelos de ML.}
    \label{fig:metricas_performance}
\end{figure}
```

### Exemplo com Subfiguras

```latex
\begin{figure}[htbp]
    \centering
    \begin{subfigure}[b]{0.45\textwidth}
        \includegraphics[width=\textwidth]{figuras/03_roc_curves_part01_curvas_roc.pdf}
        \caption{Curvas ROC completas}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.45\textwidth}
        \includegraphics[width=\textwidth]{figuras/03_roc_curves_part02_roc_zoom.pdf}
        \caption{Zoom na região ótima}
    \end{subfigure}
    \caption{Análise das curvas ROC dos modelos treinados.}
    \label{fig:roc_analysis}
\end{figure}
```

## Lista Completa de Figuras

### 01. Model Comparison (4 figuras)
- `part01`: Comparação de Métricas de Performance
- `part02`: Distribuição de Scores F2
- `part03`: Análise de Falsos Negativos
- `part04`: Radar de Performance Multidimensional

### 02. Confusion Matrices (N figuras, uma por modelo)
- `part01`: Matriz de Confusão - Modelo 1
- `part02`: Matriz de Confusão - Modelo 2
- ...

### 03. ROC Curves (3 figuras)
- `part01`: Curvas ROC - Comparação de Modelos
- `part02`: Curvas ROC - Zoom na Região Ótima
- `part03`: Ranking de Performance AUC-ROC

### 04. Precision-Recall (3 figuras)
- `part01`: Curvas Precision-Recall
- `part02`: Análise de Thresholds
- `part03`: Ranking de Performance

### 05. Feature Importance Individual (N figuras, uma por modelo)
- `part01`: Importância de Features - Modelo 1
- `part02`: Importância de Features - Modelo 2
- ...

### 06. Feature Importance Consensus (4 figuras)
- `part01`: Consenso de Importância de Features
- `part02`: Estabilidade das Features
- `part03`: Distribuição de Importância
- `part04`: Variabilidade entre Modelos

### 07. Error Probability Analysis (4 figuras)
- `part01`: Distribuição de Probabilidades por Tipo de Erro
- `part02`: Análise Detalhada de Falsos Negativos
- `part03`: Análise Detalhada de Falsos Positivos
- `part04`: Comparação Densidade de Probabilidades

### 08. Threshold Optimization (7 figuras)
- `part01`: Métricas vs Threshold
- `part02`: Evolução de Erros por Threshold
- `part03`: Trade-off Precision-Recall
- `part04`: Distribuição de Probabilidades Preditas
- `part05`: Tabela de Thresholds Recomendados
- `part06`: Análise de Sensibilidade
- `part07`: Impacto Clínico por Threshold

### 09. Base vs Optimized (6 figuras)
- `part01`: Melhorias Absolutas por Métrica
- `part02`: Melhorias Relativas Percentuais
- `part03`: Trade-off de Redução de Erros
- `part04`: Distribuição de Significância
- `part05`: Mapa de Calor das Melhorias
- `part06`: Resumo Executivo de Comparação

## Benefícios

### Para a Monografia

1. **Flexibilidade**: Use figuras individuais onde forem mais apropriadas
2. **Qualidade**: Cada figura mantém resolução máxima
3. **Organização**: Figuras nomeadas de forma clara e descritiva
4. **Múltiplos formatos**: Escolha o melhor formato para cada situação

### Para o LaTeX

1. **PDF vetorial**: Redimensionamento sem perda de qualidade
2. **SVG editável**: Possibilidade de ajustes finais
3. **PNG raster**: Preview rápido e compatibilidade universal
4. **Tamanhos otimizados**: Menos ajustes manuais necessários

## Solução de Problemas

### Figuras não são geradas

1. Verifique se `GENERATE_INDIVIDUAL_FIGURES = True`
2. Certifique-se de que a célula foi executada completamente
3. Verifique permissões de escrita na pasta de resultados

### Figuras incompletas

1. Alguns elementos complexos (tabelas especiais) podem não ser copiados perfeitamente
2. Nesse caso, a figura composta original ainda estará disponível

### Muitas figuras geradas

1. Use `GENERATE_INDIVIDUAL_FIGURES = False` para execução rápida
2. Habilite apenas quando precisar das figuras para a monografia

## Notas Técnicas

- As modificações **não alteram** o código original de geração das figuras compostas
- Figuras individuais são geradas **após** as figuras compostas
- O código é **robusto** e trata erros graciosamente
- Memória é **gerenciada** automaticamente (figuras fechadas após salvar)

## Suporte

Para problemas ou dúvidas:
1. Verifique este README primeiro
2. Revise os comentários no código do notebook
3. Teste com `GENERATE_INDIVIDUAL_FIGURES = False` para isolar problemas

---

**Última atualização**: 2024-11-24
**Versão do notebook**: 04_analysis_optimization_improved.ipynb
