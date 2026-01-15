"""
Módulo para análise de interpretabilidade com SHAP e outras técnicas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# SHAP
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️ SHAP não disponível - instalando fallback de interpretabilidade")

# Sklearn
from sklearn.inspection import permutation_importance, partial_dependence
from sklearn.tree import export_text
from sklearn.ensemble import RandomForestClassifier
import joblib

# Try to import plot_partial_dependence from multiple possible locations
try:
    from sklearn.inspection import plot_partial_dependence
    PLOT_PD_AVAILABLE = True
except ImportError:
    try:
        from sklearn.inspection._plot.partial_dependence import plot_partial_dependence
        PLOT_PD_AVAILABLE = True
    except ImportError:
        PLOT_PD_AVAILABLE = False
        print("⚠️ plot_partial_dependence não disponível - usando implementação manual")

from ..utils.config import load_config, get_results_path
from ..utils.helpers import print_section, save_figure


class ModelInterpreter:
    """
    Classe para análise de interpretabilidade de modelos de ML.
    """
    
    def __init__(self):
        """
        Inicializa o interpretador de modelos.
        """
        self.config = load_config()
        self.shap_available = SHAP_AVAILABLE
        self.explanations = {}
        self.feature_importance = {}
        self.partial_dependence_results = {}
        
    def load_model_and_data(self, model_path: str, X_test: pd.DataFrame, 
                           y_test: pd.Series, X_train: pd.DataFrame = None) -> None:
        """
        Carrega modelo e dados para análise.
        
        Args:
            model_path: Caminho para o modelo salvo
            X_test: Features de teste
            y_test: Target de teste  
            X_train: Features de treino (opcional, para SHAP)
        """
        self.model = joblib.load(model_path)
        self.X_test = X_test
        self.y_test = y_test
        self.X_train = X_train
        self.feature_names = X_test.columns.tolist()
        
        print(f"✅ Modelo carregado: {type(self.model).__name__}")
        print(f"📊 Features: {len(self.feature_names)}")
        print(f"🧪 Amostras de teste: {len(X_test)}")
        
    def analyze_feature_importance(self) -> Dict[str, pd.Series]:
        """
        Analisa importância das features usando múltiplos métodos.
        
        Returns:
            Dict com diferentes tipos de importância
        """
        print_section("ANÁLISE DE IMPORTÂNCIA DAS FEATURES")
        
        importance_results = {}
        
        # 1. Importância intrínseca do modelo (se disponível)
        if hasattr(self.model, 'feature_importances_'):
            intrinsic_importance = pd.Series(
                self.model.feature_importances_, 
                index=self.feature_names
            ).sort_values(ascending=False)
            
            importance_results['intrinsic'] = intrinsic_importance
            print(f"✅ Importância intrínseca calculada")
            
        elif hasattr(self.model, 'coef_'):
            coef_importance = pd.Series(
                np.abs(self.model.coef_[0]), 
                index=self.feature_names
            ).sort_values(ascending=False)
            
            importance_results['coefficients'] = coef_importance
            print(f"✅ Importância por coeficientes calculada")
        
        # 2. Permutation Importance
        print("🔄 Calculando Permutation Importance...")
        perm_importance = permutation_importance(
            self.model, self.X_test, self.y_test, 
            n_repeats=10, random_state=42, n_jobs=-1
        )
        
        perm_importance_series = pd.Series(
            perm_importance.importances_mean,
            index=self.feature_names
        ).sort_values(ascending=False)
        
        importance_results['permutation'] = perm_importance_series
        print(f"✅ Permutation importance calculada")
        
        # 3. SHAP Feature Importance (se disponível)
        if self.shap_available and self.X_train is not None:
            print("🔄 Calculando SHAP Feature Importance...")
            try:
                shap_importance = self._calculate_shap_importance()
                if shap_importance is not None:
                    importance_results['shap'] = shap_importance
                    print(f"✅ SHAP importance calculada")
            except Exception as e:
                print(f"⚠️ Erro no SHAP: {e}")
        
        self.feature_importance = importance_results
        return importance_results
    
    def _calculate_shap_importance(self) -> Optional[pd.Series]:
        """
        Calcula importância usando SHAP.
        """
        try:
            # Escolher explainer baseado no tipo de modelo
            if hasattr(self.model, 'predict_proba'):
                if 'RandomForest' in type(self.model).__name__ or 'XGB' in type(self.model).__name__:
                    # Tree explainer para modelos baseados em árvore
                    explainer = shap.TreeExplainer(self.model)
                    shap_values = explainer.shap_values(self.X_test.iloc[:min(500, len(self.X_test))])
                    
                    # Para classificação binária
                    if isinstance(shap_values, list):
                        shap_values = shap_values[1]  # Classe positiva
                        
                else:
                    # Explainer geral para outros modelos
                    explainer = shap.Explainer(
                        self.model.predict_proba, 
                        self.X_train.iloc[:min(100, len(self.X_train))]
                    )
                    shap_values = explainer(self.X_test.iloc[:min(500, len(self.X_test))])
                    
                    if hasattr(shap_values, 'values'):
                        # Para classificação, pegar valores da classe positiva
                        if len(shap_values.values.shape) == 3:
                            shap_values = shap_values.values[:, :, 1]
                        else:
                            shap_values = shap_values.values
                    
            else:
                return None
            
            # Calcular importância média absoluta
            if isinstance(shap_values, np.ndarray):
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
                return pd.Series(mean_abs_shap, index=self.feature_names).sort_values(ascending=False)
            
        except Exception as e:
            print(f"Erro no cálculo SHAP: {e}")
            return None
    
    def create_shap_explanations(self, n_samples: int = 100) -> Dict[str, Any]:
        """
        Cria explicações SHAP detalhadas.
        
        Args:
            n_samples: Número de amostras para análise
            
        Returns:
            Dict com explicações SHAP
        """
        if not self.shap_available:
            print("⚠️ SHAP não disponível")
            return {}
            
        print_section("CRIANDO EXPLICAÇÕES SHAP")
        
        explanations = {}
        
        try:
            # Limitar amostras para performance
            sample_size = min(n_samples, len(self.X_test))
            X_sample = self.X_test.iloc[:sample_size]
            
            print(f"🔄 Analisando {sample_size} amostras...")
            
            # Escolher explainer apropriado
            if hasattr(self.model, 'predict_proba'):
                if any(model_type in type(self.model).__name__ for model_type in ['RandomForest', 'XGB', 'LightGBM']):
                    explainer = shap.TreeExplainer(self.model)
                    shap_values = explainer.shap_values(X_sample)
                    
                    # Para classificação binária
                    if isinstance(shap_values, list):
                        shap_values = shap_values[1]
                        
                    explanations['explainer'] = explainer
                    explanations['shap_values'] = shap_values
                    explanations['expected_value'] = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
                    
                else:
                    # Usar KernelExplainer como fallback
                    background_size = min(50, len(self.X_train))
                    explainer = shap.KernelExplainer(
                        self.model.predict_proba, 
                        self.X_train.iloc[:background_size]
                    )
                    
                    shap_values = explainer.shap_values(X_sample, nsamples=50)
                    if isinstance(shap_values, list):
                        shap_values = shap_values[1]
                        
                    explanations['explainer'] = explainer
                    explanations['shap_values'] = shap_values
                    explanations['expected_value'] = explainer.expected_value
                    
            explanations['X_sample'] = X_sample
            explanations['feature_names'] = self.feature_names
            
            print(f"✅ Explicações SHAP criadas para {sample_size} amostras")
            
        except Exception as e:
            print(f"❌ Erro ao criar explicações SHAP: {e}")
            return {}
        
        self.explanations = explanations
        return explanations
    
    def analyze_partial_dependence(self, top_features: int = 10) -> Dict[str, Any]:
        """
        Analisa dependência parcial das features mais importantes.
        
        Args:
            top_features: Número de features para analisar
            
        Returns:
            Dict com resultados de partial dependence
        """
        print_section("ANÁLISE DE DEPENDÊNCIA PARCIAL")
        
        # Obter top features
        if 'intrinsic' in self.feature_importance:
            important_features = self.feature_importance['intrinsic'].head(top_features).index.tolist()
        elif 'permutation' in self.feature_importance:
            important_features = self.feature_importance['permutation'].head(top_features).index.tolist()
        else:
            important_features = self.feature_names[:top_features]
        
        print(f"🔄 Analisando dependência parcial para {len(important_features)} features...")
        
        pd_results = {}
        
        try:
            # Calcular partial dependence para cada feature
            for feature in important_features:
                feature_idx = self.feature_names.index(feature)
                
                pd_result = partial_dependence(
                    self.model, self.X_test, [feature_idx], 
                    kind='average', grid_resolution=20
                )
                
                pd_results[feature] = {
                    'values': pd_result[0][0],
                    'grid': pd_result[1][0]
                }
            
            print(f"✅ Partial dependence calculada para {len(pd_results)} features")
            
        except Exception as e:
            print(f"❌ Erro no cálculo de partial dependence: {e}")
            
        self.partial_dependence_results = pd_results
        return pd_results
    
    def create_interpretation_visualizations(self, save_plots: bool = True) -> None:
        """
        Cria visualizações de interpretabilidade.
        
        Args:
            save_plots: Se deve salvar os plots
        """
        print_section("CRIANDO VISUALIZAÇÕES DE INTERPRETABILIDADE")
        
        # Plot 1: Feature Importance Comparison
        self._plot_feature_importance_comparison(save_plots)
        
        # Plot 2: SHAP Summary (se disponível)
        if self.explanations:
            self._plot_shap_summary(save_plots)
        
        # Plot 3: Partial Dependence Plots
        if self.partial_dependence_results:
            self._plot_partial_dependence(save_plots)
        
        # Plot 4: Individual Explanations (SHAP)
        if self.explanations:
            self._plot_individual_explanations(save_plots)
    
    def _plot_feature_importance_comparison(self, save_plots: bool) -> None:
        """
        Plota comparação de diferentes métodos de importância.
        """
        if not self.feature_importance:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Feature Importance Comparison', fontsize=16, y=0.98)
        
        methods = list(self.feature_importance.keys())
        colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightyellow']
        
        for i, method in enumerate(methods[:4]):
            row, col = i // 2, i % 2
            ax = axes[row, col]
            
            top_features = self.feature_importance[method].head(15)
            
            bars = ax.barh(range(len(top_features)), top_features.values, 
                          color=colors[i], alpha=0.8)
            ax.set_yticks(range(len(top_features)))
            ax.set_yticklabels(top_features.index, fontsize=9)
            ax.set_xlabel('Importance Score')
            ax.set_title(f'{method.title()} Importance', fontsize=12, pad=15)
            ax.grid(axis='x', alpha=0.3)
            ax.invert_yaxis()
            
            # Adicionar valores nas barras
            for j, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                       f'{width:.3f}', ha='left', va='center', fontsize=8)
        
        # Se houver menos de 4 métodos, esconder subplots vazios
        for i in range(len(methods), 4):
            row, col = i // 2, i % 2
            axes[row, col].set_visible(False)
        
        plt.tight_layout()
        if save_plots:
            save_figure('feature_importance_comparison')
        plt.show()
    
    def _plot_shap_summary(self, save_plots: bool) -> None:
        """
        Cria plots de resumo SHAP.
        """
        if not self.explanations or 'shap_values' not in self.explanations:
            return
            
        try:
            fig, axes = plt.subplots(1, 2, figsize=(20, 8))
            
            # SHAP Summary Plot
            plt.subplot(1, 2, 1)
            shap.summary_plot(
                self.explanations['shap_values'],
                self.explanations['X_sample'],
                feature_names=self.feature_names,
                plot_type="bar",
                show=False
            )
            plt.title('SHAP Feature Importance', fontsize=14, pad=20)
            
            # SHAP Beeswarm Plot
            plt.subplot(1, 2, 2)
            shap.summary_plot(
                self.explanations['shap_values'],
                self.explanations['X_sample'],
                feature_names=self.feature_names,
                show=False,
                max_display=15
            )
            plt.title('SHAP Feature Impact', fontsize=14, pad=20)
            
            plt.tight_layout()
            if save_plots:
                save_figure('shap_summary_plots')
            plt.show()
            
        except Exception as e:
            print(f"❌ Erro ao plotar SHAP summary: {e}")
    
    def _plot_partial_dependence(self, save_plots: bool) -> None:
        """
        Plota gráficos de dependência parcial.
        """
        if not self.partial_dependence_results:
            return
            
        n_features = len(self.partial_dependence_results)
        n_cols = 3
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        fig.suptitle('Partial Dependence Plots', fontsize=16, y=0.98)
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, (feature, pd_data) in enumerate(self.partial_dependence_results.items()):
            row, col = i // n_cols, i % n_cols
            ax = axes[row, col]
            
            ax.plot(pd_data['grid'], pd_data['values'], 'b-', linewidth=2, alpha=0.8)
            ax.set_xlabel(feature)
            ax.set_ylabel('Partial Dependence')
            ax.set_title(f'PD: {feature}', fontsize=12, pad=15)
            ax.grid(alpha=0.3)
            
            # Adicionar linha de referência em zero
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        # Esconder subplots vazios
        for i in range(n_features, n_rows * n_cols):
            row, col = i // n_cols, i % n_cols
            axes[row, col].set_visible(False)
        
        plt.tight_layout()
        if save_plots:
            save_figure('partial_dependence_plots')
        plt.show()
    
    def _plot_individual_explanations(self, save_plots: bool, n_examples: int = 4) -> None:
        """
        Plota explicações individuais usando SHAP.
        """
        if not self.explanations or 'shap_values' not in self.explanations:
            return
            
        try:
            # Selecionar alguns exemplos interessantes
            shap_values = self.explanations['shap_values']
            X_sample = self.explanations['X_sample']
            
            # Selecionar exemplos: 2 com alta probabilidade, 2 com baixa
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X_sample)[:, 1]
                high_prob_idx = np.argsort(probabilities)[-2:]
                low_prob_idx = np.argsort(probabilities)[:2]
                selected_indices = np.concatenate([high_prob_idx, low_prob_idx])
            else:
                selected_indices = np.arange(min(n_examples, len(X_sample)))
            
            fig, axes = plt.subplots(n_examples, 1, figsize=(12, 4 * n_examples))
            fig.suptitle('Individual SHAP Explanations', fontsize=16, y=0.98)
            
            if n_examples == 1:
                axes = [axes]
            
            for i, idx in enumerate(selected_indices[:n_examples]):
                plt.subplot(n_examples, 1, i + 1)
                
                shap.waterfall_plot(
                    shap.Explanation(
                        values=shap_values[idx],
                        base_values=self.explanations['expected_value'],
                        data=X_sample.iloc[idx],
                        feature_names=self.feature_names
                    ),
                    show=False,
                    max_display=10
                )
                
                # Adicionar título com informações do paciente
                if hasattr(self.model, 'predict_proba'):
                    prob = self.model.predict_proba(X_sample.iloc[[idx]])[:, 1][0]
                    plt.title(f'Patient {idx} - Prediction Probability: {prob:.3f}', 
                             fontsize=12, pad=20)
            
            plt.tight_layout()
            if save_plots:
                save_figure('individual_shap_explanations')
            plt.show()
            
        except Exception as e:
            print(f"❌ Erro ao plotar explicações individuais: {e}")
    
    def generate_interpretation_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de interpretabilidade.
        
        Returns:
            Dict com relatório de interpretabilidade
        """
        print_section("GERANDO RELATÓRIO DE INTERPRETABILIDADE")
        
        report = {
            'model_info': {
                'model_type': type(self.model).__name__,
                'n_features': len(self.feature_names),
                'n_test_samples': len(self.X_test)
            },
            'feature_importance': self._summarize_feature_importance(),
            'top_features': self._identify_top_features(),
            'model_behavior': self._analyze_model_behavior(),
            'clinical_insights': self._extract_clinical_insights(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _summarize_feature_importance(self) -> Dict[str, Any]:
        """
        Resumo dos métodos de importância de features.
        """
        summary = {}
        
        for method, importance in self.feature_importance.items():
            summary[method] = {
                'top_5_features': importance.head(5).to_dict(),
                'mean_importance': importance.mean(),
                'std_importance': importance.std(),
                'n_important_features': (importance > importance.mean() + importance.std()).sum()
            }
        
        return summary
    
    def _identify_top_features(self) -> List[str]:
        """
        Identifica features mais importantes consistentemente.
        """
        if not self.feature_importance:
            return []
        
        # Rankear features por cada método
        rankings = {}
        for method, importance in self.feature_importance.items():
            rankings[method] = importance.rank(ascending=False)
        
        # Calcular rank médio
        if rankings:
            avg_ranking = pd.DataFrame(rankings).mean(axis=1).sort_values()
            return avg_ranking.head(10).index.tolist()
        
        return []
    
    def _analyze_model_behavior(self) -> Dict[str, Any]:
        """
        Analisa comportamento geral do modelo.
        """
        behavior = {}
        
        # Análise de partial dependence
        if self.partial_dependence_results:
            pd_trends = {}
            for feature, pd_data in self.partial_dependence_results.items():
                values = pd_data['values']
                trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                volatility = np.std(np.diff(values))
                
                pd_trends[feature] = {
                    'trend': trend,
                    'volatility': volatility,
                    'range': values.max() - values.min()
                }
            
            behavior['partial_dependence_trends'] = pd_trends
        
        # Análise SHAP (se disponível)
        if self.explanations and 'shap_values' in self.explanations:
            shap_values = self.explanations['shap_values']
            
            behavior['shap_analysis'] = {
                'mean_abs_impact': np.abs(shap_values).mean(axis=0).tolist(),
                'feature_consistency': np.std(shap_values, axis=0).tolist(),
                'positive_impact_features': (shap_values.mean(axis=0) > 0).sum(),
                'negative_impact_features': (shap_values.mean(axis=0) < 0).sum()
            }
        
        return behavior
    
    def _extract_clinical_insights(self) -> List[str]:
        """
        Extrai insights clínicos dos resultados.
        """
        insights = []
        
        # Análise baseada nas features mais importantes
        top_features = self._identify_top_features()
        
        # Categorizar features por tipo médico
        bp_features = [f for f in top_features if any(term in f.lower() for term in ['pressao', 'pam', 'pulso'])]
        anthro_features = [f for f in top_features if any(term in f.lower() for term in ['imc', 'peso', 'altura'])]
        risk_features = [f for f in top_features if any(term in f.lower() for term in ['risco', 'score', 'framingham'])]
        age_features = [f for f in top_features if 'idade' in f.lower()]
        
        if bp_features:
            insights.append(f"Features de pressão arterial são altamente preditivas: {', '.join(bp_features[:3])}")
        
        if anthro_features:
            insights.append(f"Medidas antropométricas relevantes: {', '.join(anthro_features[:2])}")
        
        if risk_features:
            insights.append(f"Scores de risco cardiovascular são importantes: {', '.join(risk_features[:2])}")
        
        if age_features:
            insights.append(f"Fatores relacionados à idade impactam predições: {', '.join(age_features[:2])}")
        
        # Análise de tendências (partial dependence)
        if self.partial_dependence_results:
            for feature, pd_data in self.partial_dependence_results.items():
                values = pd_data['values']
                if values[-1] > values[0] * 1.1:
                    insights.append(f"{feature}: Relação positiva forte com hipertensão")
                elif values[-1] < values[0] * 0.9:
                    insights.append(f"{feature}: Relação negativa com hipertensão")
        
        return insights
    
    def _generate_recommendations(self) -> List[str]:
        """
        Gera recomendações baseadas na análise.
        """
        recommendations = [
            "Focar monitoramento das features mais importantes identificadas",
            "Implementar interpretabilidade em produção para transparência clínica",
            "Validar insights clínicos com especialistas médicos",
            "Considerar features de interação para melhor compreensão",
            "Usar explicações SHAP para casos individuais em ambiente clínico"
        ]
        
        # Recomendações específicas baseadas nos resultados
        top_features = self._identify_top_features()
        
        if any('pressao' in f.lower() for f in top_features[:5]):
            recommendations.append("Pressão arterial é preditor chave - manter monitoramento contínuo")
        
        if any('idade' in f.lower() for f in top_features[:5]):
            recommendations.append("Implementar estratificação por idade para melhor precisão")
        
        if self.shap_available and self.explanations:
            recommendations.append("SHAP disponível - usar para explicações individuais de pacientes")
        
        return recommendations


def create_model_interpreter() -> ModelInterpreter:
    """
    Função de conveniência para criar interpretador de modelos.
    
    Returns:
        Instância do ModelInterpreter
    """
    return ModelInterpreter()


if __name__ == "__main__":
    print("🔍 Testando módulo ModelInterpreter...")
    
    # Criar dados de teste
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_test_data = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    y_test_data = pd.Series(np.random.choice([0, 1], n_samples))
    
    # Testar interpretador
    interpreter = ModelInterpreter()
    
    print(f"\n✅ Teste concluído!")
    print(f"🔍 ModelInterpreter pronto para uso")
    print(f"📊 SHAP {'disponível' if interpreter.shap_available else 'não disponível'}")