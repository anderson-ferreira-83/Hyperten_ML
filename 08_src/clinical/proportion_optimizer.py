"""
Otimizador de Proporções de Dados para Cenários Clínicos
Baseado na metodologia do projeto A1_A2 para otimização de proporções
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.utils import resample
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class ProportionOptimizer:
    """
    Otimizador de proporções de dados para diferentes cenários clínicos.
    Implementa metodologia similar ao projeto A1_A2.
    """
    
    def __init__(self):
        self.clinical_scenarios = {
            'screening': {
                'description': 'Cenário de triagem - alta prevalência esperada',
                'target_proportion': 0.05,  # 5% de casos positivos
                'focus': 'high_sensitivity',
                'weight_recall': 0.6,
                'weight_precision': 0.2,
                'weight_f1': 0.2
            },
            'general_population': {
                'description': 'População geral - prevalência natural',
                'target_proportion': 0.31,  # Prevalência natural do dataset
                'focus': 'balanced',
                'weight_recall': 0.4,
                'weight_precision': 0.4,
                'weight_f1': 0.2
            },
            'high_risk_cohort': {
                'description': 'Coorte de alto risco - alta prevalência',
                'target_proportion': 0.60,  # 60% de casos positivos
                'focus': 'high_specificity',
                'weight_recall': 0.2,
                'weight_precision': 0.6,
                'weight_f1': 0.2
            }
        }
        
        self.models = {
            'RF': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'GB': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'LR': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        self.optimization_results = {}
    
    def optimize_proportions_systematic(self, X, y, scenarios=None, cv_folds=5):
        """
        Otimização sistemática de proporções para múltiplos cenários clínicos.
        
        Args:
            X: Features
            y: Target
            scenarios: Lista de cenários para otimizar (default: todos)
            cv_folds: Número de folds para cross-validation
            
        Returns:
            dict: Resultados da otimização
        """
        print("🔄 Iniciando otimização sistemática de proporções...")
        
        if scenarios is None:
            scenarios = list(self.clinical_scenarios.keys())
        
        # Informações do dataset original
        original_prevalence = y.mean()
        total_samples = len(y)
        positive_samples = y.sum()
        negative_samples = (y == 0).sum()
        
        print(f"📊 Dataset original: {total_samples:,} amostras")
        print(f"   Positivos: {positive_samples:,} ({original_prevalence:.1%})")
        print(f"   Negativos: {negative_samples:,}")
        
        optimization_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': 'proportion_optimization_v2.0',
                'total_scenarios_tested': len(scenarios),
                'cv_folds': cv_folds,
                'dataset_info': {
                    'total_samples': int(total_samples),
                    'positive_samples': int(positive_samples),
                    'negative_samples': int(negative_samples),
                    'original_prevalence': float(original_prevalence)
                },
                'models_tested': list(self.models.keys()),
                'configuration': {
                    'resampling_iterations': 5,
                    'min_samples_per_class': 50
                }
            },
            'scenario_results': {},
            'best_configurations': {},
            'comparative_analysis': {}
        }
        
        # Otimizar para cada cenário
        for scenario_name in scenarios:
            scenario_config = self.clinical_scenarios[scenario_name]
            
            print(f"\n🎯 Otimizando cenário: {scenario_name}")
            print(f"   Target prevalence: {scenario_config['target_proportion']:.1%}")
            
            scenario_results = self._optimize_single_scenario(
                X, y, scenario_name, scenario_config, cv_folds
            )
            
            optimization_results['scenario_results'][scenario_name] = scenario_results
            
            print(f"✅ Cenário {scenario_name} concluído")
        
        # Encontrar melhores configurações
        optimization_results['best_configurations'] = self._find_best_configurations(
            optimization_results['scenario_results']
        )
        
        # Análise comparativa
        optimization_results['comparative_analysis'] = self._create_comparative_analysis(
            optimization_results['scenario_results']
        )
        
        self.optimization_results = optimization_results
        
        print("\n✅ Otimização de proporções concluída!")
        return optimization_results
    
    def _optimize_single_scenario(self, X, y, scenario_name, scenario_config, cv_folds):
        """Otimizar proporções para um cenário específico"""
        
        target_proportion = scenario_config['target_proportion']
        
        # Testar diferentes proporções ao redor do target
        proportions_to_test = [
            target_proportion * 0.5,   # 50% do target
            target_proportion * 0.75,  # 75% do target
            target_proportion,         # Target exato
            target_proportion * 1.25,  # 125% do target
            target_proportion * 1.5    # 150% do target
        ]
        
        # Limitar entre 0.05 e 0.95
        proportions_to_test = [max(0.05, min(0.95, p)) for p in proportions_to_test]
        proportions_to_test = list(set(proportions_to_test))  # Remover duplicatas
        
        scenario_results = {
            'scenario_config': scenario_config,
            'proportions_tested': proportions_to_test,
            'detailed_results': [],
            'best_result': None
        }
        
        for target_prop in proportions_to_test:
            print(f"   🔄 Testando proporção: {target_prop:.3f}")
            
            # Criar dataset com a proporção desejada
            X_resampled, y_resampled = self._create_proportional_dataset(
                X, y, target_prop
            )
            
            if len(X_resampled) == 0:
                continue
            
            # Testar todos os modelos
            model_results = {}
            for model_name, model in self.models.items():
                cv_scores = self._evaluate_model_cv(X_resampled, y_resampled, model, cv_folds)
                model_results[model_name] = cv_scores
            
            # Calcular score composto baseado nos pesos do cenário
            best_model, best_score = self._calculate_weighted_score(
                model_results, scenario_config
            )
            
            proportion_result = {
                'target_proportion': target_prop,
                'actual_proportion': y_resampled.mean(),
                'dataset_size': len(X_resampled),
                'best_model': best_model,
                'best_weighted_score': best_score,
                'model_results': model_results,
                'variability_metrics': self._calculate_variability_metrics(model_results)
            }
            
            scenario_results['detailed_results'].append(proportion_result)
        
        # Encontrar melhor resultado para o cenário
        if scenario_results['detailed_results']:
            best = max(scenario_results['detailed_results'], 
                      key=lambda x: x['best_weighted_score'])
            scenario_results['best_result'] = best
        
        return scenario_results
    
    def _create_proportional_dataset(self, X, y, target_proportion, min_samples=100):
        """Criar dataset com proporção específica"""
        
        positive_indices = np.where(y == 1)[0]
        negative_indices = np.where(y == 0)[0]
        
        # Calcular número de amostras necessárias
        if target_proportion >= 0.5:
            # Se target > 50%, limitar pelos positivos disponíveis
            n_positive = len(positive_indices)
            n_negative = int(n_positive * (1 - target_proportion) / target_proportion)
            n_negative = min(n_negative, len(negative_indices))
        else:
            # Se target < 50%, limitar pelos negativos disponíveis
            n_negative = len(negative_indices)
            n_positive = int(n_negative * target_proportion / (1 - target_proportion))
            n_positive = min(n_positive, len(positive_indices))
        
        # Verificar se temos amostras suficientes
        if n_positive < 25 or n_negative < 25:
            return pd.DataFrame(), pd.Series()
        
        # Amostrar indices
        selected_positive = np.random.choice(positive_indices, size=n_positive, replace=False)
        selected_negative = np.random.choice(negative_indices, size=n_negative, replace=False)
        
        selected_indices = np.concatenate([selected_positive, selected_negative])
        np.random.shuffle(selected_indices)
        
        return X.iloc[selected_indices], y.iloc[selected_indices]
    
    def _evaluate_model_cv(self, X, y, model, cv_folds):
        """Avaliar modelo com cross-validation"""
        
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        scores = {
            'accuracy': cross_val_score(model, X, y, cv=cv, scoring='accuracy').mean(),
            'precision': cross_val_score(model, X, y, cv=cv, scoring='precision').mean(),
            'recall': cross_val_score(model, X, y, cv=cv, scoring='recall').mean(),
            'f1': cross_val_score(model, X, y, cv=cv, scoring='f1').mean(),
            'roc_auc': cross_val_score(model, X, y, cv=cv, scoring='roc_auc').mean()
        }
        
        return scores
    
    def _calculate_weighted_score(self, model_results, scenario_config):
        """Calcular score ponderado baseado no cenário"""
        
        best_model = None
        best_score = -1
        
        weights = {
            'recall': scenario_config['weight_recall'],
            'precision': scenario_config['weight_precision'],
            'f1': scenario_config['weight_f1']
        }
        
        for model_name, scores in model_results.items():
            weighted_score = (
                scores['recall'] * weights['recall'] +
                scores['precision'] * weights['precision'] +
                scores['f1'] * weights['f1']
            )
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_model = model_name
        
        return best_model, best_score
    
    def _calculate_variability_metrics(self, model_results):
        """Calcular métricas de variabilidade entre modelos"""
        
        # Coletar todas as métricas
        all_scores = []
        for model_scores in model_results.values():
            all_scores.extend([
                model_scores['accuracy'],
                model_scores['precision'],
                model_scores['recall'],
                model_scores['f1'],
                model_scores['roc_auc']
            ])
        
        return {
            'mean_score': np.mean(all_scores),
            'std_score': np.std(all_scores),
            'min_score': np.min(all_scores),
            'max_score': np.max(all_scores),
            'score_range': np.max(all_scores) - np.min(all_scores)
        }
    
    def _find_best_configurations(self, scenario_results):
        """Encontrar melhores configurações por cenário"""
        
        best_configs = {}
        
        for scenario_name, results in scenario_results.items():
            if results['best_result']:
                best_configs[scenario_name] = {
                    'scenario': scenario_name,
                    'optimal_proportion': results['best_result']['target_proportion'],
                    'actual_proportion': results['best_result']['actual_proportion'],
                    'best_model': results['best_result']['best_model'],
                    'weighted_score': results['best_result']['best_weighted_score'],
                    'dataset_size': results['best_result']['dataset_size'],
                    'recommendation': self._generate_scenario_recommendation(
                        scenario_name, results['best_result']
                    )
                }
        
        return best_configs
    
    def _generate_scenario_recommendation(self, scenario_name, best_result):
        """Gerar recomendação para o cenário"""
        
        model = best_result['best_model']
        score = best_result['best_weighted_score']
        proportion = best_result['target_proportion']
        
        if score > 0.8:
            quality = "excelente"
        elif score > 0.7:
            quality = "boa"
        elif score > 0.6:
            quality = "aceitável"
        else:
            quality = "baixa"
        
        return (f"Para {scenario_name}, usar {model} com proporção {proportion:.1%} "
                f"oferece performance {quality} (score: {score:.3f})")
    
    def _create_comparative_analysis(self, scenario_results):
        """Criar análise comparativa entre cenários"""
        
        analysis = {
            'proportion_range': {},
            'model_performance': {},
            'stability_analysis': {},
            'recommendations': {}
        }
        
        # Análise de faixas de proporção
        all_proportions = []
        for results in scenario_results.values():
            if results['best_result']:
                all_proportions.append(results['best_result']['target_proportion'])
        
        if all_proportions:
            analysis['proportion_range'] = {
                'min_proportion': min(all_proportions),
                'max_proportion': max(all_proportions),
                'mean_proportion': np.mean(all_proportions),
                'std_proportion': np.std(all_proportions)
            }
        
        # Análise de performance por modelo
        model_performance = {}
        for scenario_name, results in scenario_results.items():
            if results['best_result']:
                model = results['best_result']['best_model']
                if model not in model_performance:
                    model_performance[model] = []
                model_performance[model].append(results['best_result']['best_weighted_score'])
        
        analysis['model_performance'] = {
            model: {
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'scenarios_won': len(scores)
            }
            for model, scores in model_performance.items()
        }
        
        return analysis
    
    def create_proportion_visualizations(self, save_path=None):
        """Criar visualizações da otimização de proporções"""
        
        if not self.optimization_results:
            print("❌ Nenhuma otimização executada ainda")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Análise de Otimização de Proporções por Cenário Clínico', fontsize=16, y=0.98)
        
        # 1. Proporções ótimas por cenário
        ax1 = axes[0, 0]
        scenarios = list(self.optimization_results['best_configurations'].keys())
        proportions = [self.optimization_results['best_configurations'][s]['optimal_proportion'] 
                      for s in scenarios]
        
        bars = ax1.bar(scenarios, proportions, color=['lightblue', 'lightgreen', 'lightcoral'])
        ax1.set_ylabel('Proporção Ótima')
        ax1.set_title('Proporções Ótimas por Cenário')
        ax1.grid(axis='y', alpha=0.3)
        
        for bar, prop in zip(bars, proportions):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{prop:.1%}', ha='center', va='bottom')
        
        # 2. Performance por modelo
        ax2 = axes[0, 1]
        model_perf = self.optimization_results['comparative_analysis']['model_performance']
        models = list(model_perf.keys())
        mean_scores = [model_perf[m]['mean_score'] for m in models]
        std_scores = [model_perf[m]['std_score'] for m in models]
        
        ax2.bar(models, mean_scores, yerr=std_scores, capsize=5, 
               color=['skyblue', 'lightgreen', 'salmon'])
        ax2.set_ylabel('Score Médio')
        ax2.set_title('Performance Média por Modelo')
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Cenários ganhos por modelo
        ax3 = axes[0, 2]
        scenarios_won = [model_perf[m]['scenarios_won'] for m in models]
        ax3.pie(scenarios_won, labels=models, autopct='%1.0f', startangle=90,
               colors=['skyblue', 'lightgreen', 'salmon'])
        ax3.set_title('Cenários Vencidos por Modelo')
        
        # 4. Análise detalhada por cenário
        ax4 = axes[1, 0]
        
        # Selecionar primeiro cenário para análise detalhada
        first_scenario = list(self.optimization_results['scenario_results'].keys())[0]
        scenario_data = self.optimization_results['scenario_results'][first_scenario]
        
        if scenario_data['detailed_results']:
            proportions_tested = [r['target_proportion'] for r in scenario_data['detailed_results']]
            weighted_scores = [r['best_weighted_score'] for r in scenario_data['detailed_results']]
            
            ax4.plot(proportions_tested, weighted_scores, 'o-', linewidth=2, markersize=8)
            ax4.set_xlabel('Proporção Testada')
            ax4.set_ylabel('Score Ponderado')
            ax4.set_title(f'Análise Detalhada: {first_scenario}')
            ax4.grid(alpha=0.3)
        
        # 5. Comparação de tamanhos de dataset
        ax5 = axes[1, 1]
        dataset_sizes = [self.optimization_results['best_configurations'][s]['dataset_size'] 
                        for s in scenarios]
        
        ax5.bar(scenarios, dataset_sizes, color=['lightblue', 'lightgreen', 'lightcoral'])
        ax5.set_ylabel('Tamanho do Dataset')
        ax5.set_title('Tamanho do Dataset por Cenário')
        ax5.grid(axis='y', alpha=0.3)
        
        # 6. Heatmap de scores por cenário e modelo
        ax6 = axes[1, 2]
        
        # Construir matriz de scores
        score_matrix = []
        for scenario in scenarios:
            scenario_results = self.optimization_results['scenario_results'][scenario]
            if scenario_results['best_result']:
                model_results = scenario_results['best_result']['model_results']
                row = [model_results.get(model, {}).get('f1', 0) for model in ['RF', 'GB', 'LR']]
                score_matrix.append(row)
        
        if score_matrix:
            sns.heatmap(score_matrix, annot=True, fmt='.3f', cmap='RdYlBu_r',
                       xticklabels=['RF', 'GB', 'LR'], yticklabels=scenarios, ax=ax6)
            ax6.set_title('Heatmap F1-Score: Cenários vs Modelos')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'proportion_optimization_analysis.png', dpi=300, bbox_inches='tight')
            print(f"📊 Visualizações salvas em: {save_path}")
        
        plt.show()
        return fig
    
    def save_optimization_results(self, save_path):
        """Salvar resultados da otimização"""
        
        if not self.optimization_results:
            print("❌ Nenhuma otimização executada ainda")
            return
        
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar resultados completos
        with open(save_path / 'proportion_optimization_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Salvar resumo das melhores configurações
        best_configs = []
        for scenario, config in self.optimization_results['best_configurations'].items():
            best_configs.append(config)
        
        df_best = pd.DataFrame(best_configs)
        df_best.to_csv(save_path / 'best_proportions_summary.csv', index=False)
        
        # Salvar resultados detalhados
        detailed_results = []
        for scenario_name, scenario_data in self.optimization_results['scenario_results'].items():
            for result in scenario_data['detailed_results']:
                row = {
                    'scenario': scenario_name,
                    'target_proportion': result['target_proportion'],
                    'actual_proportion': result['actual_proportion'],
                    'dataset_size': result['dataset_size'],
                    'best_model': result['best_model'],
                    'best_weighted_score': result['best_weighted_score']
                }
                detailed_results.append(row)
        
        df_detailed = pd.DataFrame(detailed_results)
        df_detailed.to_csv(save_path / 'proportion_optimization_detailed.csv', index=False)
        
        print(f"💾 Resultados salvos em: {save_path}")
        return save_path