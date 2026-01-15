#!/usr/bin/env python3
"""
Teste da Validação Clínica - Versão Simplificada
Demonstra o sistema de validação implementado
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json

def simulate_clinical_validation():
    """Simular validação clínica com dados disponíveis"""
    
    print("🚀 TESTE DE VALIDAÇÃO CLÍNICA AUTOMATIZADA")
    print("Baseado na metodologia do projeto A1_A2")
    print("="*80)
    
    # Simular carregamento de dados
    print("📁 Simulando carregamento de modelo e dados...")
    
    # Usar dados disponíveis
    data_path = Path('results/data/feature_engineered_enhanced_selected.csv')
    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"✅ Dados carregados: {df.shape}")
    else:
        print("❌ Dados não encontrados, criando dados sintéticos para demonstração...")
        
        # Criar dados sintéticos para demonstração
        np.random.seed(42)
        n_samples = 1000
        
        df = pd.DataFrame({
            'score_risco_cv': np.random.normal(0.5, 0.2, n_samples),
            'pressao_sistolica': np.random.normal(130, 20, n_samples),
            'pressao_diastolica': np.random.normal(85, 10, n_samples),
            'pressao_arterial_media': np.random.normal(100, 15, n_samples),
            'idade': np.random.normal(50, 15, n_samples),
            'risco_hipertensao': np.random.binomial(1, 0.3, n_samples)
        })
        print(f"✅ Dados sintéticos criados: {df.shape}")
    
    # Separar features e target
    target_col = 'risco_hipertensao'
    if target_col not in df.columns:
        target_col = df.columns[-1]
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print(f"✅ Features: {X.shape[1]}, Target: {target_col}")
    print(f"📊 Distribuição target: {dict(y.value_counts())}")
    
    # Simular predições de modelo
    print("\n📊 Simulando predições do modelo...")
    
    # Simular probabilidades baseadas nas features (correlação realística)
    y_proba = np.random.beta(2, 5, len(y))  # Distribuição mais realística
    
    # Adicionar correlação com features importantes
    if 'pressao_sistolica' in X.columns:
        # Correlação positiva com pressão sistólica
        systolic_norm = (X['pressao_sistolica'] - X['pressao_sistolica'].min()) / (X['pressao_sistolica'].max() - X['pressao_sistolica'].min())
        y_proba = 0.7 * y_proba + 0.3 * systolic_norm
    
    y_proba = np.clip(y_proba, 0.01, 0.99)  # Limitar entre 0.01 e 0.99
    y_pred = (y_proba > 0.5).astype(int)
    
    print("✅ Predições simuladas geradas")
    
    # Executar validações
    results = run_validation_demo(X, y, y_pred, y_proba, df)
    
    # Salvar resultados
    save_demo_results(results)
    
    print(f"\n✅ DEMONSTRAÇÃO DE VALIDAÇÃO CLÍNICA CONCLUÍDA!")
    return results

def run_validation_demo(X, y, y_pred, y_proba, df):
    """Executar demonstração das validações"""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'demo_mode': True,
        'validations': {}
    }
    
    # 1. Validação Médica Básica
    print(f"\n🔍 1. VALIDAÇÃO CONTRA CONHECIMENTO MÉDICO")
    print("-" * 50)
    
    medical_validation = validate_medical_logic(X, y, y_pred, y_proba)
    results['validations']['medical'] = medical_validation
    
    print(f"📊 Score de consistência médica: {medical_validation['consistency_score']:.3f}")
    print(f"📋 {medical_validation['interpretation']}")
    
    # 2. Análise de Thresholds
    print(f"\n⚖️ 2. ANÁLISE DE THRESHOLDS CLÍNICOS")
    print("-" * 50)
    
    threshold_analysis = analyze_thresholds(y, y_proba)
    results['validations']['thresholds'] = threshold_analysis
    
    print(f"📊 THRESHOLDS ANALISADOS:")
    for scenario, metrics in threshold_analysis['scenarios'].items():
        print(f"   {scenario}: {metrics['threshold']:.3f} "
              f"(Sens: {metrics['sensitivity']:.1%}, Spec: {metrics['specificity']:.1%})")
    
    # 3. Análise de Proporções
    print(f"\n📊 3. ANÁLISE DE PROPORÇÕES")
    print("-" * 50)
    
    proportion_analysis = analyze_proportions(y, y_proba)
    results['validations']['proportions'] = proportion_analysis
    
    print(f"📊 CENÁRIOS ANALISADOS:")
    for scenario, config in proportion_analysis['scenarios'].items():
        print(f"   {scenario}: {config['target_prevalence']:.1%} "
              f"(Performance estimada: {config['estimated_performance']:.3f})")
    
    return results

def validate_medical_logic(X, y, y_pred, y_proba):
    """Validação básica da lógica médica"""
    
    validation = {
        'features_analyzed': list(X.columns),
        'correlations': {},
        'consistency_score': 0,
        'interpretation': ''
    }
    
    # Analisar correlações com features médicas importantes
    medical_features = {
        'pressao_sistolica': 'Pressão Sistólica',
        'pressao_diastolica': 'Pressão Diastólica', 
        'pressao_arterial_media': 'Pressão Arterial Média',
        'idade': 'Idade',
        'score_risco': 'Score de Risco'
    }
    
    correlations_found = 0
    total_correlations = 0
    
    for feature_key, feature_name in medical_features.items():
        # Buscar features que contenham a palavra-chave
        matching_features = [f for f in X.columns if feature_key.lower() in f.lower()]
        
        if matching_features:
            feature = matching_features[0]  # Usar primeira correspondência
            
            # Calcular correlação com predições
            try:
                correlation = np.corrcoef(X[feature], y_proba)[0, 1]
                
                validation['correlations'][feature_name] = {
                    'feature_used': feature,
                    'correlation': correlation,
                    'expected_positive': True,  # Esperamos correlação positiva
                    'meets_expectation': correlation > 0.1
                }
                
                if correlation > 0.1:
                    correlations_found += 1
                total_correlations += 1
                
            except Exception as e:
                validation['correlations'][feature_name] = {
                    'error': str(e)
                }
    
    # Calcular score de consistência
    if total_correlations > 0:
        consistency_score = correlations_found / total_correlations
    else:
        consistency_score = 0
    
    validation['consistency_score'] = consistency_score
    
    # Interpretação
    if consistency_score >= 0.7:
        validation['interpretation'] = "Excelente consistência com conhecimento médico"
    elif consistency_score >= 0.5:
        validation['interpretation'] = "Boa consistência médica"
    elif consistency_score >= 0.3:
        validation['interpretation'] = "Consistência médica moderada"
    else:
        validation['interpretation'] = "Baixa consistência médica - revisão recomendada"
    
    return validation

def analyze_thresholds(y_true, y_proba):
    """Análise básica de thresholds"""
    
    from sklearn.metrics import confusion_matrix
    
    scenarios = {
        'screening': {
            'description': 'Triagem - Alta Sensibilidade',
            'threshold': 0.3
        },
        'balanced': {
            'description': 'Diagnóstico Balanceado',
            'threshold': 0.5
        },
        'confirmation': {
            'description': 'Confirmação - Alta Especificidade',
            'threshold': 0.7
        }
    }
    
    threshold_analysis = {
        'scenarios': {}
    }
    
    for scenario_name, scenario_config in scenarios.items():
        threshold = scenario_config['threshold']
        y_pred_thresh = (y_proba >= threshold).astype(int)
        
        # Calcular métricas
        try:
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred_thresh).ravel()
            
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            
            threshold_analysis['scenarios'][scenario_name] = {
                'threshold': threshold,
                'description': scenario_config['description'],
                'sensitivity': sensitivity,
                'specificity': specificity,
                'accuracy': accuracy,
                'confusion_matrix': {'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn)}
            }
            
        except Exception as e:
            threshold_analysis['scenarios'][scenario_name] = {
                'threshold': threshold,
                'error': str(e)
            }
    
    return threshold_analysis

def analyze_proportions(y, y_proba):
    """Análise básica de proporções"""
    
    current_prevalence = y.mean()
    
    scenarios = {
        'screening': {
            'target_prevalence': 0.05,
            'description': 'Cenário de triagem populacional'
        },
        'general': {
            'target_prevalence': current_prevalence,
            'description': 'População geral (prevalência atual)'
        },
        'high_risk': {
            'target_prevalence': 0.60,
            'description': 'Coorte de alto risco'
        }
    }
    
    proportion_analysis = {
        'current_prevalence': current_prevalence,
        'scenarios': {}
    }
    
    for scenario_name, scenario_config in scenarios.items():
        # Simular performance baseada na diferença da prevalência atual
        target_prev = scenario_config['target_prevalence']
        
        # Estimar performance (simulação simplificada)
        prevalence_diff = abs(target_prev - current_prevalence)
        
        # Performance decresce com maior diferença da prevalência atual
        estimated_performance = max(0.5, 1.0 - prevalence_diff * 2)
        
        proportion_analysis['scenarios'][scenario_name] = {
            'target_prevalence': target_prev,
            'description': scenario_config['description'],
            'prevalence_difference': prevalence_diff,
            'estimated_performance': estimated_performance,
            'recommendation': get_proportion_recommendation(prevalence_diff, estimated_performance)
        }
    
    return proportion_analysis

def get_proportion_recommendation(prevalence_diff, performance):
    """Gerar recomendação baseada na diferença de prevalência"""
    
    if prevalence_diff < 0.1:
        return "Cenário ótimo - baixa adaptação necessária"
    elif prevalence_diff < 0.2:
        return "Cenário bom - adaptação moderada necessária"
    elif prevalence_diff < 0.3:
        return "Cenário aceitável - adaptação significativa necessária"
    else:
        return "Cenário desafiador - retreinamento pode ser necessário"

def save_demo_results(results):
    """Salvar resultados da demonstração"""
    
    save_path = Path('3_CLINICAL_VALIDATION')
    save_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salvar resultados completos
    with open(save_path / f'clinical_validation_demo_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    # Criar resumo
    summary = f"""
DEMONSTRAÇÃO DE VALIDAÇÃO CLÍNICA AUTOMATIZADA
=============================================

Data/Hora: {results['timestamp']}
Modo: Demonstração

RESULTADOS DA VALIDAÇÃO:
{'-'*40}

1. VALIDAÇÃO MÉDICA:
   Score de Consistência: {results['validations']['medical']['consistency_score']:.3f}
   Interpretação: {results['validations']['medical']['interpretation']}

2. ANÁLISE DE THRESHOLDS:
"""
    
    for scenario, metrics in results['validations']['thresholds']['scenarios'].items():
        if 'error' not in metrics:
            summary += f"""   {scenario.upper()}:
     Threshold: {metrics['threshold']:.3f}
     Sensibilidade: {metrics['sensitivity']:.1%}
     Especificidade: {metrics['specificity']:.1%}
     Acurácia: {metrics['accuracy']:.1%}

"""
    
    summary += "3. ANÁLISE DE PROPORÇÕES:\n"
    for scenario, config in results['validations']['proportions']['scenarios'].items():
        summary += f"""   {scenario.upper()}:
     Prevalência Alvo: {config['target_prevalence']:.1%}
     Performance Estimada: {config['estimated_performance']:.3f}
     Recomendação: {config['recommendation']}

"""
    
    summary += f"""
CONCLUSÃO:
{'-'*40}
✅ Sistema de validação clínica implementado com sucesso!
✅ Estrutura baseada na metodologia do projeto A1_A2
✅ Validação médica, thresholds e proporções analisados
✅ Resultados salvos para análise posterior

Arquivos gerados:
- clinical_validation_demo_{timestamp}.json
- clinical_validation_demo_summary_{timestamp}.txt

Para uso em produção, conecte com modelo real e execute:
python clinical_validation_runner.py
"""
    
    with open(save_path / f'clinical_validation_demo_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n💾 Resultados da demonstração salvos em: {save_path}")
    print(f"   📄 clinical_validation_demo_{timestamp}.json")
    print(f"   📄 clinical_validation_demo_summary_{timestamp}.txt")

if __name__ == "__main__":
    results = simulate_clinical_validation()