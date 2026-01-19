#!/usr/bin/env python3
"""
Script de Validação Clínica Automatizada
Executa validação completa baseada na metodologia do projeto A1_A2
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'src'))

# Imports dos módulos de validação
try:
    from clinical.clinical_validator import ClinicalValidator
    from clinical.threshold_optimizer import ThresholdOptimizer
    from clinical.proportion_optimizer import ProportionOptimizer
    print("✅ Módulos de validação clínica carregados")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


def load_model_and_data():
    """Carregar modelo e dados para validação"""
    
    print("📁 Carregando modelo e dados...")
    
    # Caminhos dos arquivos
    model_path = project_root / '02_notebooks' / '06_model_metrics' / '3_GradientBoosting' / 'All_Features' / 'Gradient_Boosting.pkl'
    scaler_path = project_root / '02_notebooks' / '06_model_metrics' / '3_GradientBoosting' / 'All_Features' / 'feature_scaler.pkl'
    data_path = project_root / 'results' / 'data' / 'feature_engineered_enhanced_selected.csv'
    
    # Verificar se arquivos existem
    if not model_path.exists():
        print(f"❌ Modelo não encontrado: {model_path}")
        return None, None, None, None, None
    
    if not data_path.exists():
        print(f"❌ Dados não encontrados: {data_path}")
        return None, None, None, None, None
    
    try:
        # Carregar modelo
        model = joblib.load(model_path)
        print(f"✅ Modelo carregado: {type(model).__name__}")
        
        # Carregar scaler se disponível
        scaler = None
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            print("✅ Scaler carregado")
        
        # Carregar dados
        df = pd.read_csv(data_path)
        print(f"✅ Dados carregados: {df.shape}")
        
        # Separar features e target
        target_col = 'risco_hipertensao'
        if target_col not in df.columns:
            # Procurar coluna target alternativa
            possible_targets = ['Risk', 'TenYearCHD', 'target']
            for col in possible_targets:
                if col in df.columns:
                    target_col = col
                    break
            else:
                target_col = df.columns[-1]  # Usar última coluna
                print(f"⚠️ Target padrão não encontrado, usando: {target_col}")
        
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        print(f"✅ Features: {X.shape[1]}, Target: {target_col}")
        print(f"📊 Distribuição target: {dict(y.value_counts())}")
        
        return model, scaler, df, X, y
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivos: {e}")
        return None, None, None, None, None


def run_clinical_validation(model, df, X, y, scaler=None):
    """Executar validação clínica completa"""
    
    print("\n" + "="*80)
    print("🏥 INICIANDO VALIDAÇÃO CLÍNICA AUTOMATIZADA")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'model_type': type(model).__name__,
        'validation_results': {},
        'threshold_optimization': {},
        'proportion_optimization': {},
        'summary': {}
    }
    
    # Preparar dados
    X_scaled = X.copy()
    if scaler is not None:
        X_scaled = pd.DataFrame(
            scaler.transform(X), 
            columns=X.columns, 
            index=X.index
        )
        print("✅ Dados escalonados aplicados")
    
    # Fazer predições
    try:
        y_pred = model.predict(X_scaled)
        y_proba = model.predict_proba(X_scaled)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        print("✅ Predições geradas")
    except Exception as e:
        print(f"❌ Erro nas predições: {e}")
        return results
    
    # 1. Validação contra conhecimento médico
    print(f"\n🔍 1. VALIDAÇÃO CONTRA CONHECIMENTO MÉDICO")
    print("-" * 50)
    
    try:
        validator = ClinicalValidator()
        
        # Obter feature importance
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = pd.Series(model.feature_importances_, index=X.columns)
        
        validation_results = validator.validate_against_medical_knowledge(
            df, y_proba, feature_importance
        )
        
        results['validation_results'] = validation_results
        
        # Mostrar resumo
        consistency_score = validation_results['medical_consistency']['overall_consistency_score']
        print(f"📊 Score de consistência médica: {consistency_score:.3f}")
        print(f"📋 Interpretação: {validation_results['medical_consistency']['interpretation']}")
        
    except Exception as e:
        print(f"❌ Erro na validação médica: {e}")
        results['validation_results'] = {'error': str(e)}
    
    # 2. Otimização de thresholds
    print(f"\n⚖️ 2. OTIMIZAÇÃO DE THRESHOLDS CLÍNICOS")
    print("-" * 50)
    
    try:
        threshold_optimizer = ThresholdOptimizer()
        
        threshold_results = threshold_optimizer.optimize_thresholds_systematic(y, y_proba)
        results['threshold_optimization'] = threshold_results
        
        # Mostrar resumo dos melhores thresholds
        print(f"\n📊 MELHORES THRESHOLDS:")
        for scenario, config in threshold_results['best_thresholds'].items():
            print(f"   {scenario}: {config['threshold']:.3f} "
                  f"(Sens: {config['sensitivity']:.1%}, Spec: {config['specificity']:.1%})")
        
    except Exception as e:
        print(f"❌ Erro na otimização de thresholds: {e}")
        results['threshold_optimization'] = {'error': str(e)}
    
    # 3. Otimização de proporções
    print(f"\n📊 3. OTIMIZAÇÃO DE PROPORÇÕES")
    print("-" * 50)
    
    try:
        proportion_optimizer = ProportionOptimizer()
        
        proportion_results = proportion_optimizer.optimize_proportions_systematic(X, y)
        results['proportion_optimization'] = proportion_results
        
        # Mostrar resumo das melhores proporções
        print(f"\n📊 MELHORES PROPORÇÕES:")
        for scenario, config in proportion_results['best_configurations'].items():
            print(f"   {scenario}: {config['optimal_proportion']:.1%} "
                  f"(Modelo: {config['best_model']}, Score: {config['weighted_score']:.3f})")
        
    except Exception as e:
        print(f"❌ Erro na otimização de proporções: {e}")
        results['proportion_optimization'] = {'error': str(e)}
    
    # 4. Resumo executivo
    print(f"\n📋 4. RESUMO EXECUTIVO")
    print("-" * 50)
    
    summary = generate_executive_summary(results)
    results['summary'] = summary
    
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    return results


def generate_executive_summary(results):
    """Gerar resumo executivo dos resultados"""
    
    summary = {}
    
    # Resumo da validação médica
    if 'validation_results' in results and 'medical_consistency' in results['validation_results']:
        consistency_score = results['validation_results']['medical_consistency']['overall_consistency_score']
        
        if consistency_score >= 0.8:
            summary['Consistência Médica'] = f"Excelente ({consistency_score:.3f})"
        elif consistency_score >= 0.6:
            summary['Consistência Médica'] = f"Boa ({consistency_score:.3f})"
        else:
            summary['Consistência Médica'] = f"Precisa melhorias ({consistency_score:.3f})"
    
    # Resumo dos thresholds
    if 'threshold_optimization' in results and 'best_thresholds' in results['threshold_optimization']:
        thresholds = results['threshold_optimization']['best_thresholds']
        
        if 'screening' in thresholds:
            screening_sens = thresholds['screening']['sensitivity']
            summary['Threshold Screening'] = f"{thresholds['screening']['threshold']:.3f} (Sens: {screening_sens:.1%})"
        
        if 'confirmation' in thresholds:
            confirmation_spec = thresholds['confirmation']['specificity']
            summary['Threshold Confirmação'] = f"{thresholds['confirmation']['threshold']:.3f} (Spec: {confirmation_spec:.1%})"
    
    # Resumo das proporções
    if 'proportion_optimization' in results and 'best_configurations' in results['proportion_optimization']:
        configs = results['proportion_optimization']['best_configurations']
        
        if 'general_population' in configs:
            pop_config = configs['general_population']
            summary['Proporção Ótima'] = f"{pop_config['optimal_proportion']:.1%} ({pop_config['best_model']})"
    
    # Status geral
    errors = []
    if 'error' in results.get('validation_results', {}):
        errors.append('validação')
    if 'error' in results.get('threshold_optimization', {}):
        errors.append('thresholds')
    if 'error' in results.get('proportion_optimization', {}):
        errors.append('proporções')
    
    if not errors:
        summary['Status Geral'] = "✅ Validação completa"
    else:
        summary['Status Geral'] = f"⚠️ Erros em: {', '.join(errors)}"
    
    return summary


def save_validation_results(results, save_path=None):
    """Salvar resultados da validação"""
    
    if save_path is None:
        save_path = project_root / '3_CLINICAL_VALIDATION'
    
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Salvar resultados completos
    import json
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(save_path / f'clinical_validation_complete_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    # Salvar resumo executivo
    summary_content = f"""
RELATÓRIO DE VALIDAÇÃO CLÍNICA AUTOMATIZADA
==========================================

Data/Hora: {results['timestamp']}
Modelo: {results['model_type']}

RESUMO EXECUTIVO:
{'-'*40}
"""
    
    for key, value in results['summary'].items():
        summary_content += f"{key}: {value}\n"
    
    summary_content += f"""

DETALHES DA VALIDAÇÃO:
{'-'*40}
"""
    
    # Adicionar detalhes dos thresholds se disponível
    if 'best_thresholds' in results.get('threshold_optimization', {}):
        summary_content += "\nTHRESHOLDS CLÍNICOS ÓTIMOS:\n"
        for scenario, config in results['threshold_optimization']['best_thresholds'].items():
            summary_content += f"- {scenario.title()}: {config['threshold']:.3f}\n"
            summary_content += f"  Sensibilidade: {config['sensitivity']:.1%}\n"
            summary_content += f"  Especificidade: {config['specificity']:.1%}\n\n"
    
    # Adicionar detalhes das proporções se disponível
    if 'best_configurations' in results.get('proportion_optimization', {}):
        summary_content += "PROPORÇÕES ÓTIMAS POR CENÁRIO:\n"
        for scenario, config in results['proportion_optimization']['best_configurations'].items():
            summary_content += f"- {scenario.title()}: {config['optimal_proportion']:.1%}\n"
            summary_content += f"  Melhor modelo: {config['best_model']}\n"
            summary_content += f"  Score: {config['weighted_score']:.3f}\n\n"
    
    with open(save_path / f'clinical_validation_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"\n💾 Resultados salvos em: {save_path}")
    print(f"   📄 clinical_validation_complete_{timestamp}.json")
    print(f"   📄 clinical_validation_summary_{timestamp}.txt")
    
    return save_path


def main():
    """Função principal"""
    
    print("🚀 SCRIPT DE VALIDAÇÃO CLÍNICA AUTOMATIZADA")
    print("Baseado na metodologia do projeto A1_A2")
    print("="*80)
    
    # Carregar modelo e dados
    model, scaler, df, X, y = load_model_and_data()
    
    if model is None:
        print("❌ Falha ao carregar dados necessários")
        return 1
    
    # Executar validação
    results = run_clinical_validation(model, df, X, y, scaler)
    
    # Salvar resultados
    save_path = save_validation_results(results)
    
    print(f"\n✅ VALIDAÇÃO CLÍNICA CONCLUÍDA!")
    print(f"📁 Resultados salvos em: {save_path}")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
