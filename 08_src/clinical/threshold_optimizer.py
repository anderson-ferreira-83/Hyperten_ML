"""
Otimizador de Thresholds Clínicos
Inspirado na estrutura de otimização do projeto A1_A2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
from datetime import datetime
from pathlib import Path


class ThresholdOptimizer:
    """
    Otimizador de thresholds para diferentes cenários clínicos.
    Similar ao sistema de otimização de proporções do projeto A1_A2.
    """
    
    def __init__(self):
        self.clinical_scenarios = {
            'screening': {
                'description': 'Triagem inicial - minimizar falsos negativos',
                'priority': 'high_sensitivity',
                'target_sensitivity': 0.90,
                'min_specificity': 0.70
            },
            'diagnosis': {
                'description': 'Diagnóstico balanceado - otimizar F1',
                'priority': 'balanced',
                'target_f1': 0.80,
                'min_accuracy': 0.75
            },
            'confirmation': {
                'description': 'Confirmação diagnóstica - minimizar falsos positivos',
                'priority': 'high_specificity',
                'target_specificity': 0.95,
                'min_sensitivity': 0.60
            }
        }
        
        self.optimization_results = {}
    
    def optimize_thresholds_systematic(self, y_true, y_proba, scenarios=None):
        """
        Otimização sistemática de thresholds para múltiplos cenários.
        Baseado na metodologia do projeto A1_A2.
        
        Args:
            y_true: Labels verdadeiros
            y_proba: Probabilidades preditas
            scenarios: Lista de cenários para otimizar (default: todos)
            
        Returns:
            dict: Resultados da otimização
        """
        print("🔄 Iniciando otimização sistemática de thresholds...")
        
        if scenarios is None:
            scenarios = list(self.clinical_scenarios.keys())
        
        # Testar diferentes thresholds
        thresholds_to_test = np.arange(0.1, 0.95, 0.05)
        
        optimization_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': 'threshold_optimization_v2.0',
                'total_thresholds_tested': len(thresholds_to_test),
                'scenarios_optimized': scenarios,
                'sample_info': {
                    'total_samples': len(y_true),
                    'positive_samples': int(y_true.sum()),
                    'negative_samples': int((y_true == 0).sum()),
                    'prevalence': float(y_true.mean())
                }
            },
            'detailed_results': {},
            'best_thresholds': {},
            'comparative_analysis': {}
        }
        
        # Calcular métricas para cada threshold
        detailed_metrics = []
        
        for threshold in thresholds_to_test:
            y_pred = (y_proba >= threshold).astype(int)
            
            # Matriz de confusão
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            
            # Métricas clínicas
            metrics = {
                'threshold': float(threshold),
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, zero_division=0),
                'sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
                'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
                'ppv': tp / (tp + fp) if (tp + fp) > 0 else 0,  # Valor Preditivo Positivo
                'npv': tn / (tn + fn) if (tn + fn) > 0 else 0,  # Valor Preditivo Negativo
                'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
                'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
                'confusion_matrix': {'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn)}
            }
            
            detailed_metrics.append(metrics)
        
        optimization_results['detailed_results'] = detailed_metrics
        
        # Otimizar para cada cenário clínico
        for scenario in scenarios:
            best_threshold = self._optimize_for_scenario(
                detailed_metrics, scenario, self.clinical_scenarios[scenario]
            )
            optimization_results['best_thresholds'][scenario] = best_threshold
            
            print(f"✅ Cenário {scenario}: threshold ótimo = {best_threshold['threshold']:.3f}")
        
        # Análise comparativa
        optimization_results['comparative_analysis'] = self._create_comparative_analysis(
            optimization_results['best_thresholds']
        )
        
        self.optimization_results = optimization_results
        
        print("✅ Otimização de thresholds concluída!")
        return optimization_results
    
    def _optimize_for_scenario(self, detailed_metrics, scenario_name, scenario_config):
        """Otimizar threshold para cenário específico"""
        
        if scenario_config['priority'] == 'high_sensitivity':
            # Priorizar sensibilidade alta
            valid_metrics = [m for m in detailed_metrics 
                           if m['sensitivity'] >= scenario_config['target_sensitivity']
                           and m['specificity'] >= scenario_config['min_specificity']]
            
            if valid_metrics:
                # Entre os que atendem os critérios, escolher melhor especificidade
                best = max(valid_metrics, key=lambda x: x['specificity'])
            else:
                # Se não há válidos, pegar o melhor sensitivity
                best = max(detailed_metrics, key=lambda x: x['sensitivity'])
        
        elif scenario_config['priority'] == 'high_specificity':
            # Priorizar especificidade alta
            valid_metrics = [m for m in detailed_metrics 
                           if m['specificity'] >= scenario_config['target_specificity']
                           and m['sensitivity'] >= scenario_config['min_sensitivity']]
            
            if valid_metrics:
                # Entre os que atendem os critérios, escolher melhor sensibilidade
                best = max(valid_metrics, key=lambda x: x['sensitivity'])
            else:
                # Se não há válidos, pegar o melhor specificity
                best = max(detailed_metrics, key=lambda x: x['specificity'])
        
        else:  # balanced
            # Priorizar F1-score
            valid_metrics = [m for m in detailed_metrics 
                           if m['accuracy'] >= scenario_config['min_accuracy']]
            
            if valid_metrics:
                best = max(valid_metrics, key=lambda x: x['f1_score'])
            else:
                best = max(detailed_metrics, key=lambda x: x['f1_score'])
        
        # Adicionar informações do cenário
        best_result = best.copy()
        best_result['scenario'] = scenario_name
        best_result['scenario_config'] = scenario_config
        best_result['meets_criteria'] = self._check_scenario_criteria(best, scenario_config)
        
        return best_result
    
    def _check_scenario_criteria(self, metrics, config):
        """Verificar se métricas atendem critérios do cenário"""
        if config['priority'] == 'high_sensitivity':
            return (metrics['sensitivity'] >= config['target_sensitivity'] and 
                   metrics['specificity'] >= config['min_specificity'])
        elif config['priority'] == 'high_specificity':
            return (metrics['specificity'] >= config['target_specificity'] and 
                   metrics['sensitivity'] >= config['min_sensitivity'])
        else:  # balanced
            return (metrics['f1_score'] >= config['target_f1'] and 
                   metrics['accuracy'] >= config['min_accuracy'])
    
    def _create_comparative_analysis(self, best_thresholds):
        """Criar análise comparativa entre cenários"""
        comparison = {
            'threshold_range': {
                'min': min(t['threshold'] for t in best_thresholds.values()),
                'max': max(t['threshold'] for t in best_thresholds.values()),
                'spread': max(t['threshold'] for t in best_thresholds.values()) - 
                         min(t['threshold'] for t in best_thresholds.values())
            },
            'performance_tradeoffs': {},
            'clinical_recommendations': {}
        }
        
        # Análise de trade-offs
        for scenario, results in best_thresholds.items():
            comparison['performance_tradeoffs'][scenario] = {
                'sensitivity_vs_specificity': {
                    'sensitivity': results['sensitivity'],
                    'specificity': results['specificity'],
                    'balance_score': 2 * (results['sensitivity'] * results['specificity']) / 
                                   (results['sensitivity'] + results['specificity'])
                },
                'ppv_npv': {
                    'ppv': results['ppv'],
                    'npv': results['npv']
                }
            }
        
        # Recomendações clínicas
        for scenario, results in best_thresholds.items():
            if results['meets_criteria']:
                recommendation = f"Threshold {results['threshold']:.3f} atende critérios clínicos"
            else:
                recommendation = f"Threshold {results['threshold']:.3f} é o melhor disponível, mas não atende todos os critérios"
            
            comparison['clinical_recommendations'][scenario] = {
                'recommendation': recommendation,
                'use_case': self.clinical_scenarios[scenario]['description']
            }
        
        return comparison
    
    def create_optimization_visualizations(self, save_path=None):
        """Criar visualizações da otimização de thresholds"""
        if not self.optimization_results:
            print("❌ Nenhuma otimização executada ainda")
            return
        
        # Preparar dados para visualização
        df_metrics = pd.DataFrame(self.optimization_results['detailed_results'])
        
        # Criar subplot
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Análise de Otimização de Thresholds Clínicos', fontsize=16, y=0.98)
        
        # 1. Sensibilidade vs Especificidade
        ax1 = axes[0, 0]
        ax1.plot(df_metrics['threshold'], df_metrics['sensitivity'], 'b-', label='Sensibilidade', linewidth=2)
        ax1.plot(df_metrics['threshold'], df_metrics['specificity'], 'r-', label='Especificidade', linewidth=2)
        
        # Marcar thresholds ótimos
        for scenario, results in self.optimization_results['best_thresholds'].items():
            ax1.axvline(x=results['threshold'], color='gray', linestyle='--', alpha=0.7)
            ax1.text(results['threshold'], 0.9, scenario[:4], rotation=90, fontsize=8)
        
        ax1.set_xlabel('Threshold')
        ax1.set_ylabel('Score')
        ax1.set_title('Sensibilidade vs Especificidade')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. F1-Score e Accuracy
        ax2 = axes[0, 1]
        ax2.plot(df_metrics['threshold'], df_metrics['f1_score'], 'g-', label='F1-Score', linewidth=2)
        ax2.plot(df_metrics['threshold'], df_metrics['accuracy'], 'orange', label='Accuracy', linewidth=2)
        ax2.set_xlabel('Threshold')
        ax2.set_ylabel('Score')
        ax2.set_title('F1-Score e Accuracy')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # 3. VPP e VPN
        ax3 = axes[0, 2]
        ax3.plot(df_metrics['threshold'], df_metrics['ppv'], 'm-', label='VPP', linewidth=2)
        ax3.plot(df_metrics['threshold'], df_metrics['npv'], 'c-', label='VPN', linewidth=2)
        ax3.set_xlabel('Threshold')
        ax3.set_ylabel('Valor Preditivo')
        ax3.set_title('Valores Preditivos (VPP e VPN)')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # 4. Comparação de cenários
        ax4 = axes[1, 0]
        scenarios = list(self.optimization_results['best_thresholds'].keys())
        thresholds = [self.optimization_results['best_thresholds'][s]['threshold'] for s in scenarios]
        sensitivities = [self.optimization_results['best_thresholds'][s]['sensitivity'] for s in scenarios]
        
        bars = ax4.bar(scenarios, thresholds, color=['lightblue', 'lightgreen', 'lightcoral'])
        ax4.set_ylabel('Threshold Ótimo')
        ax4.set_title('Thresholds Ótimos por Cenário')
        ax4.grid(axis='y', alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, threshold in zip(bars, thresholds):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{threshold:.3f}', ha='center', va='bottom')
        
        # 5. Heatmap de métricas por cenário
        ax5 = axes[1, 1]
        metrics_matrix = []
        metric_names = ['sensitivity', 'specificity', 'f1_score', 'accuracy']
        
        for scenario in scenarios:
            row = [self.optimization_results['best_thresholds'][scenario][metric] for metric in metric_names]
            metrics_matrix.append(row)
        
        sns.heatmap(metrics_matrix, annot=True, fmt='.3f', cmap='RdYlBu_r',
                   xticklabels=[m.replace('_', ' ').title() for m in metric_names],
                   yticklabels=scenarios, ax=ax5)
        ax5.set_title('Heatmap de Performance por Cenário')
        
        # 6. Distribuição de False Positives e False Negatives
        ax6 = axes[1, 2]
        fp_rates = [self.optimization_results['best_thresholds'][s]['false_positive_rate'] for s in scenarios]
        fn_rates = [self.optimization_results['best_thresholds'][s]['false_negative_rate'] for s in scenarios]
        
        x = np.arange(len(scenarios))
        width = 0.35
        
        ax6.bar(x - width/2, fp_rates, width, label='Taxa FP', color='red', alpha=0.7)
        ax6.bar(x + width/2, fn_rates, width, label='Taxa FN', color='blue', alpha=0.7)
        ax6.set_xlabel('Cenário')
        ax6.set_ylabel('Taxa de Erro')
        ax6.set_title('Taxas de Falsos Positivos e Negativos')
        ax6.set_xticks(x)
        ax6.set_xticklabels(scenarios)
        ax6.legend()
        ax6.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'threshold_optimization_analysis.png', dpi=300, bbox_inches='tight')
            print(f"📊 Visualizações salvas em: {save_path / 'threshold_optimization_analysis.png'}")
        
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
        with open(save_path / 'threshold_optimization_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Salvar CSV com métricas detalhadas
        df_detailed = pd.DataFrame(self.optimization_results['detailed_results'])
        df_detailed.to_csv(save_path / 'threshold_optimization_detailed.csv', index=False)
        
        # Salvar resumo dos melhores thresholds
        best_summary = []
        for scenario, results in self.optimization_results['best_thresholds'].items():
            summary = {
                'scenario': scenario,
                'threshold': results['threshold'],
                'sensitivity': results['sensitivity'],
                'specificity': results['specificity'],
                'f1_score': results['f1_score'],
                'accuracy': results['accuracy'],
                'ppv': results['ppv'],
                'npv': results['npv'],
                'meets_criteria': results['meets_criteria']
            }
            best_summary.append(summary)
        
        df_summary = pd.DataFrame(best_summary)
        df_summary.to_csv(save_path / 'best_thresholds_summary.csv', index=False)
        
        print(f"💾 Resultados salvos em: {save_path}")
        print(f"   📄 threshold_optimization_results.json")
        print(f"   📄 threshold_optimization_detailed.csv")
        print(f"   📄 best_thresholds_summary.csv")
        
        return save_path