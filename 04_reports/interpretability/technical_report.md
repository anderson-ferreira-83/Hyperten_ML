
# 🔬 Relatório Técnico - Interpretabilidade do Modelo

## 📊 Especificações Técnicas
- **Modelo**: RandomForestClassifier
- **Features**: 12
- **Amostras de Treino**: 3,740
- **Amostras de Teste**: 936
- **Balanceamento**: 50.0% classe positiva

## 🔍 Métodos de Interpretabilidade
- **Feature Importance**: intrinsic, permutation
- **SHAP**: Implementado
- **Partial Dependence**: 6 features analisadas
- **Permutation Importance**: Validação cruzada

## 📈 Resultados Detalhados
### Performance Metrics:
- **AUC-ROC**: 0.9679
- **F1-Score**: 0.9126
- **Precisão**: 0.9106
- **Recall**: 0.9145

### Feature Engineering Impact:
- Features originais vs. engineered na seleção final
- Contribuição de features médicas especializadas
- Validação de conhecimento clínico incorporado

## 🏥 Validação Médica
- Análise por grupos de risco cardiovascular
- Estratificação por faixas etárias
- Comparação com diretrizes clínicas estabelecidas
- Interpretação de casos mal classificados

## 📁 Arquivos Gerados
- `interpretability_report.json`: Análise completa
- `clinical_thresholds_analysis.csv`: Análise de thresholds
- `clinical_category_importance.csv`: Importância por categoria
- `feature_importance_*.csv`: Múltiplos métodos
- `final_predictions_with_explanations.csv`: Predições explicadas

## 🔧 Reprodutibilidade
- Random seed: 42
- Versões de bibliotecas documentadas
- Pipeline completo versionado
- Configurações em arquivos YAML

---
*Relatório técnico gerado em 14/01/2026 10:41*
