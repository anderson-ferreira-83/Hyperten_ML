#!/usr/bin/env python3
"""
Demonstração do Feature Engineering Médico Avançado
Baseado na metodologia do projeto A1_A2
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'src'))

try:
    from feature_engineering.medical_feature_engineer import MedicalFeatureEngineer
    print("✅ Módulo de feature engineering médico carregado")
except ImportError as e:
    print(f"❌ Erro ao importar módulo: {e}")
    sys.exit(1)


def run_medical_feature_engineering_demo():
    """Executar demonstração completa do feature engineering médico"""
    
    print("🧬 DEMONSTRAÇÃO DE FEATURE ENGINEERING MÉDICO AVANÇADO")
    print("Baseado na metodologia do projeto A1_A2")
    print("="*80)
    
    # 1. Carregar dados
    print("📁 Carregando dados para feature engineering...")
    
    data_path = Path('results/data/feature_engineered_enhanced_selected.csv')
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"✅ Dados carregados: {df.shape}")
        
        # Mostrar informações básicas do dataset
        print(f"📊 Colunas disponíveis: {len(df.columns)}")
        print(f"   Features numéricas: {len(df.select_dtypes(include=[np.number]).columns)}")
        print(f"   Features categóricas: {len(df.select_dtypes(exclude=[np.number]).columns)}")
        
    else:
        print("❌ Dados não encontrados, criando dados sintéticos para demonstração...")
        
        # Criar dados sintéticos realísticos para demonstração
        np.random.seed(42)
        n_samples = 2000
        
        df = pd.DataFrame({
            'age': np.random.normal(50, 15, n_samples).clip(18, 85),
            'sysBP': np.random.normal(130, 20, n_samples).clip(90, 200),
            'diaBP': np.random.normal(85, 12, n_samples).clip(60, 120),
            'totChol': np.random.normal(220, 40, n_samples).clip(120, 400),
            'BMI': np.random.normal(26, 4, n_samples).clip(15, 45),
            'glucose': np.random.normal(95, 15, n_samples).clip(70, 200),
            'heartRate': np.random.normal(75, 12, n_samples).clip(50, 120),
            'cigsPerDay': np.random.poisson(5, n_samples).clip(0, 40),
            'prevalentHyp': np.random.binomial(1, 0.3, n_samples),
            'risco_hipertensao': np.random.binomial(1, 0.31, n_samples)
        })
        
        # Adicionar algumas correlações realísticas
        df.loc[df['age'] > 60, 'sysBP'] += np.random.normal(15, 5, (df['age'] > 60).sum())
        df.loc[df['BMI'] > 30, 'sysBP'] += np.random.normal(10, 3, (df['BMI'] > 30).sum())
        
        print(f"✅ Dados sintéticos criados: {df.shape}")
    
    # 2. Inicializar feature engineer
    print("\n🔧 Inicializando Medical Feature Engineer...")
    engineer = MedicalFeatureEngineer()
    
    # Mostrar informações do dataset original
    target_col = 'risco_hipertensao'
    if target_col not in df.columns:
        possible_targets = ['Risk', 'TenYearCHD', 'prevalentHyp']
        for col in possible_targets:
            if col in df.columns:
                target_col = col
                break
        else:
            target_col = df.columns[-1]
    
    print(f"📊 Dataset original:")
    print(f"   Target: {target_col}")
    print(f"   Features: {df.shape[1] - 1}")
    print(f"   Amostras: {df.shape[0]:,}")
    print(f"   Distribuição target: {dict(df[target_col].value_counts())}")
    
    # 3. Executar feature engineering
    print(f"\n🧬 Executando feature engineering médico avançado...")
    
    df_original = df.copy()
    df_engineered = engineer.engineer_comprehensive_features(df)
    
    # 4. Análise dos resultados
    print(f"\n📊 RESULTADOS DO FEATURE ENGINEERING:")
    print("-" * 50)
    
    features_originais = df_original.shape[1]
    features_engenheiradas = df_engineered.shape[1]
    features_criadas = features_engenheiradas - features_originais
    
    print(f"✅ Features originais: {features_originais}")
    print(f"✅ Features após engineering: {features_engenheiradas}")
    print(f"🆕 Novas features criadas: {features_criadas}")
    print(f"📈 Aumento percentual: {(features_criadas / features_originais) * 100:.1f}%")
    
    # 5. Relatório detalhado
    report = engineer.get_feature_engineering_report()
    
    print(f"\n📋 RELATÓRIO DETALHADO:")
    print("-" * 50)
    print(f"📊 Total de features criadas: {report['total_features_created']}")
    print(f"\n🏥 Por categoria médica:")
    for categoria, quantidade in report['feature_categories'].items():
        print(f"   {categoria}: {quantidade} features")
    
    print(f"\n🧠 Conhecimento médico aplicado:")
    for knowledge_area in report['medical_knowledge_applied']:
        print(f"   ✅ {knowledge_area}")
    
    # 6. Seleção de features relevantes
    print(f"\n🎯 Executando seleção de features relevantes...")
    
    relevant_features = engineer.select_relevant_features(df_engineered, target_col, correlation_threshold=0.05)
    
    # Criar dataset final com features selecionadas
    df_final = df_engineered[relevant_features + [target_col]].copy()
    
    print(f"✅ Features selecionadas: {len(relevant_features)}")
    print(f"📊 Dataset final: {df_final.shape}")
    
    # 7. Análise de correlação das novas features
    print(f"\n📈 Analisando correlações das novas features...")
    
    # Correlações das features criadas com o target
    new_features = [f for f in engineer.created_features if f in df_engineered.columns]
    if new_features:
        correlations = df_engineered[new_features + [target_col]].corr()[target_col].abs().sort_values(ascending=False)
        correlations = correlations[correlations.index != target_col]
        
        print(f"\n🔝 TOP 10 NOVAS FEATURES POR CORRELAÇÃO:")
        for i, (feature, corr) in enumerate(correlations.head(10).items(), 1):
            print(f"   {i:2d}. {feature}: {corr:.4f}")
    
    # 8. Salvar resultados
    save_path = save_feature_engineering_results(df_final, report, correlations if new_features else None)
    
    # 9. Resumo executivo
    print(f"\n📋 RESUMO EXECUTIVO:")
    print("=" * 50)
    
    print(f"✅ FEATURE ENGINEERING MÉDICO CONCLUÍDO:")
    print(f"   🧬 {features_criadas} novas features médicas criadas")
    print(f"   🎯 {len(relevant_features)} features relevantes selecionadas")
    print(f"   📊 Dataset final otimizado: {df_final.shape}")
    print(f"   🏥 Conhecimento médico especializado aplicado")
    
    print(f"\n🚀 BENEFÍCIOS ALCANÇADOS:")
    print(f"   📈 Expansão inteligente do espaço de features")
    print(f"   🏥 Features baseadas em diretrizes médicas")
    print(f"   🎯 Seleção automática de features relevantes")
    print(f"   🧠 Aplicação de conhecimento clínico especializado")
    print(f"   📊 Preparação para modelos de alta performance")
    
    print(f"\n💾 Resultados salvos em: {save_path}")
    
    return df_final, report


def save_feature_engineering_results(df_final, report, correlations):
    """Salvar resultados do feature engineering"""
    
    save_path = Path('results/feature_engineering')
    save_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Salvar dataset final
    df_final.to_csv(save_path / f'medical_features_engineered_{timestamp}.csv', index=False)
    
    # 2. Salvar relatório completo
    import json
    with open(save_path / f'feature_engineering_report_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # 3. Salvar relatório em texto
    report_content = f"""
RELATÓRIO DE FEATURE ENGINEERING MÉDICO AVANÇADO
===============================================

Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Metodologia: Baseada no projeto A1_A2
Versão: Medical Feature Engineering v2.0

RESUMO GERAL:
============
Total de features criadas: {report['total_features_created']}

CATEGORIAS DE FEATURES CRIADAS:
==============================
"""
    
    for categoria, quantidade in report['feature_categories'].items():
        report_content += f"- {categoria.replace('_', ' ').title()}: {quantidade} features\n"
    
    report_content += f"""
FEATURES CRIADAS:
================
"""
    
    for i, feature in enumerate(report['created_features'], 1):
        report_content += f"{i:2d}. {feature}\n"
    
    if correlations is not None:
        report_content += f"""
TOP 15 FEATURES POR CORRELAÇÃO COM TARGET:
==========================================
"""
        for i, (feature, corr) in enumerate(correlations.head(15).items(), 1):
            report_content += f"{i:2d}. {feature}: {corr:.4f}\n"
    
    report_content += f"""
CONHECIMENTO MÉDICO APLICADO:
============================
"""
    
    for knowledge_area in report['medical_knowledge_applied']:
        report_content += f"✅ {knowledge_area.replace('_', ' ').title()}\n"
    
    report_content += f"""
METODOLOGIA APLICADA:
====================
1. Análise de Features de Pressão Arterial:
   - Cálculo de MAP (Mean Arterial Pressure)
   - Pressão de pulso e índices derivados
   - Categorização segundo AHA/ACC 2017
   - Features de desvio da normalidade

2. Features de Risco Cardiovascular:
   - Categorização por faixas etárias
   - Scores de risco metabólico
   - Índices compostos de risco

3. Features de Interação Médica:
   - Interações multiplicativas entre features importantes
   - Razões clinicamente relevantes
   - Scores compostos baseados em guidelines

4. Features Polinomiais e Transformações:
   - Expansões polinomiais de features importantes
   - Transformações não-lineares
   - Features de magnitude e escala

5. Seleção Inteligente de Features:
   - Correlação com target
   - Importância médica prioritária
   - Balanceamento entre quantidade e qualidade

CONCLUSÕES:
===========
✅ Feature engineering médico aplicado com sucesso
✅ Conhecimento clínico especializado incorporado
✅ Features relevantes selecionadas automaticamente
✅ Dataset otimizado para modelos de alta performance
✅ Metodologia reproduzível e cientificamente fundamentada

ARQUIVOS GERADOS:
================
- medical_features_engineered_{timestamp}.csv
- feature_engineering_report_{timestamp}.json
- feature_engineering_summary_{timestamp}.txt

Para aplicar em produção:
python feature_engineering_medical_demo.py

===============================================
Relatório gerado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sistema TCC Hipertensão ML v3.0 - Feature Engineering Médico
===============================================
"""
    
    with open(save_path / f'feature_engineering_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n💾 Arquivos salvos:")
    print(f"   📄 medical_features_engineered_{timestamp}.csv")
    print(f"   📄 feature_engineering_report_{timestamp}.json")
    print(f"   📄 feature_engineering_summary_{timestamp}.txt")
    
    return save_path


if __name__ == "__main__":
    df_final, report = run_medical_feature_engineering_demo()