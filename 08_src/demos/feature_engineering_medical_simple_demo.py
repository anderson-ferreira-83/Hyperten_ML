#!/usr/bin/env python3
"""
Demonstração Simplificada do Feature Engineering Médico Avançado
Versão sem dependências externas
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json


def run_medical_feature_engineering_simple():
    """Executar demonstração simplificada do feature engineering médico"""
    
    print("🧬 DEMONSTRAÇÃO DE FEATURE ENGINEERING MÉDICO AVANÇADO")
    print("Versão simplificada - sem dependências externas")
    print("Baseado na metodologia do projeto A1_A2")
    print("="*80)
    
    # 1. Carregar ou criar dados
    print("📁 Carregando dados para feature engineering...")
    
    data_path = Path('results/data/feature_engineered_enhanced_selected.csv')
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"✅ Dados carregados: {df.shape}")
        
    else:
        print("📊 Criando dados sintéticos realísticos para demonstração...")
        
        # Criar dados sintéticos médicos realísticos
        np.random.seed(42)
        n_samples = 2000
        
        # Simular dados médicos com distribuições realísticas
        age = np.random.normal(50, 15, n_samples)
        age = np.clip(age, 18, 85)
        
        # Pressão sistólica correlacionada com idade
        sysBP = 110 + (age - 30) * 0.8 + np.random.normal(0, 15, n_samples)
        sysBP = np.clip(sysBP, 90, 200)
        
        # Pressão diastólica correlacionada com sistólica
        diaBP = 60 + (sysBP - 110) * 0.6 + np.random.normal(0, 8, n_samples)
        diaBP = np.clip(diaBP, 50, 120)
        
        # Colesterol com variação por idade
        totChol = 180 + (age - 40) * 1.2 + np.random.normal(0, 30, n_samples)
        totChol = np.clip(totChol, 120, 400)
        
        # BMI com distribuição realística
        BMI = np.random.lognormal(3.2, 0.3, n_samples)
        BMI = np.clip(BMI, 15, 45)
        
        # Glucose correlacionado com BMI e idade
        glucose = 80 + (BMI - 25) * 2 + (age - 40) * 0.3 + np.random.normal(0, 12, n_samples)
        glucose = np.clip(glucose, 70, 300)
        
        # Target baseado em regras médicas realísticas
        risk_score = (
            (age > 55) * 0.3 +
            (sysBP > 140) * 0.4 +
            (diaBP > 90) * 0.3 +
            (BMI > 30) * 0.2 +
            (totChol > 240) * 0.2 +
            np.random.normal(0, 0.15, n_samples)
        )
        
        risco_hipertensao = (risk_score > 0.5).astype(int)
        
        df = pd.DataFrame({
            'age': age,
            'sysBP': sysBP,
            'diaBP': diaBP,
            'totChol': totChol,
            'BMI': BMI,
            'glucose': glucose,
            'heartRate': np.random.normal(75, 12, n_samples).clip(50, 120),
            'cigsPerDay': np.random.poisson(3, n_samples).clip(0, 40),
            'prevalentHyp': (sysBP > 140).astype(int) | (diaBP > 90).astype(int),
            'risco_hipertensao': risco_hipertensao
        })
        
        print(f"✅ Dados sintéticos criados: {df.shape}")
    
    # Informações do dataset original
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
    
    # 2. Executar feature engineering médico
    print(f"\n🧬 Executando feature engineering médico avançado...")
    
    df_original = df.copy()
    df_engineered = engineer_medical_features(df)
    
    # 3. Análise dos resultados
    print(f"\n📊 RESULTADOS DO FEATURE ENGINEERING:")
    print("-" * 50)
    
    features_originais = df_original.shape[1]
    features_engenheiradas = df_engineered.shape[1]
    features_criadas = features_engenheiradas - features_originais
    
    print(f"✅ Features originais: {features_originais}")
    print(f"✅ Features após engineering: {features_engenheiradas}")
    print(f"🆕 Novas features criadas: {features_criadas}")
    print(f"📈 Aumento percentual: {(features_criadas / features_originais) * 100:.1f}%")
    
    # 4. Análise de correlação
    print(f"\n📈 Analisando correlações das novas features...")
    
    # Identificar features criadas
    new_features = [col for col in df_engineered.columns if col not in df_original.columns]
    
    if new_features:
        correlations = df_engineered[new_features + [target_col]].corr()[target_col].abs()
        correlations = correlations[correlations.index != target_col].sort_values(ascending=False)
        
        print(f"\n🔝 TOP 10 NOVAS FEATURES POR CORRELAÇÃO:")
        for i, (feature, corr) in enumerate(correlations.head(10).items(), 1):
            print(f"   {i:2d}. {feature}: {corr:.4f}")
    
    # 5. Seleção de features relevantes
    print(f"\n🎯 Executando seleção de features relevantes...")
    
    relevant_features = select_relevant_features(df_engineered, target_col, threshold=0.05)
    df_final = df_engineered[relevant_features + [target_col]].copy()
    
    print(f"✅ Features selecionadas: {len(relevant_features)}")
    print(f"📊 Dataset final: {df_final.shape}")
    
    # 6. Gerar relatório
    report = generate_feature_engineering_report(df_original, df_engineered, new_features, correlations)
    
    # 7. Salvar resultados
    save_path = save_results(df_final, report)
    
    # 8. Resumo executivo
    print(f"\n📋 RESUMO EXECUTIVO:")
    print("=" * 50)
    
    print(f"✅ FEATURE ENGINEERING MÉDICO CONCLUÍDO:")
    print(f"   🧬 {features_criadas} novas features médicas criadas")
    print(f"   🎯 {len(relevant_features)} features relevantes selecionadas") 
    print(f"   📊 Dataset final otimizado: {df_final.shape}")
    print(f"   🏥 Conhecimento médico especializado aplicado")
    
    print(f"\n🚀 BENEFÍCIOS ALCANÇADOS:")
    print(f"   📈 Expansão inteligente do espaço de features")
    print(f"   🏥 Features baseadas em diretrizes médicas (AHA/ACC)")
    print(f"   🎯 Seleção automática de features relevantes")
    print(f"   🧠 Aplicação de conhecimento clínico especializado")
    print(f"   📊 Preparação para modelos de alta performance")
    
    print(f"\n💾 Resultados salvos em: {save_path}")
    
    return df_final, report


def engineer_medical_features(df):
    """Criar features médicas avançadas"""
    
    df_eng = df.copy()
    created_features = []
    
    # 1. Features de pressão arterial avançadas
    print("   🩺 Criando features de pressão arterial...")
    
    if 'sysBP' in df.columns and 'diaBP' in df.columns:
        # Pressão arterial média (MAP)
        df_eng['MAP_calculada'] = df_eng['diaBP'] + (df_eng['sysBP'] - df_eng['diaBP']) / 3
        
        # Pressão de pulso
        df_eng['pressao_pulso'] = df_eng['sysBP'] - df_eng['diaBP']
        
        # Índice de pressão arterial
        df_eng['indice_PA'] = (df_eng['sysBP'] / 120 + df_eng['diaBP'] / 80) / 2
        
        # Categoria de hipertensão AHA/ACC 2017
        df_eng['categoria_hipertensao'] = df_eng.apply(
            lambda row: classify_blood_pressure_aha(row['sysBP'], row['diaBP']), axis=1
        )
        
        # Hipertensão sistólica isolada
        df_eng['hipertensao_sistolica_isolada'] = ((df_eng['sysBP'] >= 140) & (df_eng['diaBP'] < 90)).astype(int)
        
        # Desvio da pressão normal
        df_eng['desvio_PA_sys'] = df_eng['sysBP'] - 120
        df_eng['desvio_PA_dia'] = df_eng['diaBP'] - 80
        
        # Score de pressão ponderado
        df_eng['score_PA_ponderado'] = ((df_eng['sysBP'] - 90) * 0.6 + (df_eng['diaBP'] - 60) * 0.4) / 100
        
        created_features.extend([
            'MAP_calculada', 'pressao_pulso', 'indice_PA', 'categoria_hipertensao',
            'hipertensao_sistolica_isolada', 'desvio_PA_sys', 'desvio_PA_dia', 'score_PA_ponderado'
        ])
    
    # 2. Features de risco cardiovascular
    print("   ❤️ Criando features de risco cardiovascular...")
    
    if 'age' in df.columns:
        # Faixa etária de risco
        df_eng['faixa_etaria_risco'] = pd.cut(
            df_eng['age'], 
            bins=[0, 35, 45, 55, 65, 100],
            labels=[0, 1, 2, 3, 4]  # Usar números para evitar problemas
        ).astype(int)
        
        # Score de idade normalizado
        df_eng['score_idade_norm'] = (df_eng['age'] - 20) / 60
        
        # Risco exponencial por idade
        df_eng['risco_exp_idade'] = np.exp((df_eng['age'] - 40) / 20)
        
        created_features.extend(['faixa_etaria_risco', 'score_idade_norm', 'risco_exp_idade'])
    
    # 3. Features de BMI
    if 'BMI' in df.columns:
        # Categoria de BMI
        df_eng['categoria_BMI'] = pd.cut(
            df_eng['BMI'],
            bins=[0, 18.5, 25, 30, 35, 100],
            labels=[0, 1, 2, 3, 4]  # Usar números
        ).astype(int)
        
        # Desvio do BMI normal
        df_eng['desvio_BMI_normal'] = abs(df_eng['BMI'] - 22.5)
        
        # Risco metabólico por BMI
        df_eng['risco_metabolico_BMI'] = np.where(
            df_eng['BMI'] >= 30, 2,
            np.where(df_eng['BMI'] >= 25, 1, 0)
        )
        
        created_features.extend(['categoria_BMI', 'desvio_BMI_normal', 'risco_metabolico_BMI'])
    
    # 4. Features de colesterol
    if 'totChol' in df.columns:
        # Categoria de colesterol
        df_eng['categoria_colesterol'] = pd.cut(
            df_eng['totChol'],
            bins=[0, 200, 240, 500],
            labels=[0, 1, 2]  # Usar números
        ).astype(int)
        
        # Score de risco por colesterol
        df_eng['score_risco_colesterol'] = (df_eng['totChol'] - 150) / 100
        
        created_features.extend(['categoria_colesterol', 'score_risco_colesterol'])
    
    # 5. Features de interação médica
    print("   🔄 Criando features de interação médica...")
    
    # Interações importantes
    if 'sysBP' in df.columns and 'diaBP' in df.columns:
        df_eng['razao_sys_dia'] = df_eng['sysBP'] / df_eng['diaBP']
        created_features.append('razao_sys_dia')
    
    if 'age' in df.columns and 'sysBP' in df.columns:
        df_eng['interacao_idade_PA'] = df_eng['age'] * df_eng['sysBP'] / 1000  # Normalizar
        df_eng['razao_idade_PA'] = df_eng['age'] / df_eng['sysBP']
        created_features.extend(['interacao_idade_PA', 'razao_idade_PA'])
    
    if 'BMI' in df.columns and 'sysBP' in df.columns:
        df_eng['interacao_BMI_PA'] = df_eng['BMI'] * df_eng['sysBP'] / 1000  # Normalizar
        created_features.append('interacao_BMI_PA')
    
    # 6. Scores compostos
    print("   🎯 Criando scores compostos...")
    
    # Score de Framingham simplificado
    framingham_score = np.zeros(len(df_eng))
    
    if 'age' in df.columns:
        framingham_score += np.where(df_eng['age'] >= 60, 2, np.where(df_eng['age'] >= 45, 1, 0))
    
    if 'sysBP' in df.columns:
        framingham_score += np.where(df_eng['sysBP'] >= 160, 3, 
                                    np.where(df_eng['sysBP'] >= 140, 2, 
                                           np.where(df_eng['sysBP'] >= 130, 1, 0)))
    
    if 'totChol' in df.columns:
        framingham_score += np.where(df_eng['totChol'] >= 240, 2, 
                                    np.where(df_eng['totChol'] >= 200, 1, 0))
    
    df_eng['score_framingham_simpl'] = framingham_score
    created_features.append('score_framingham_simpl')
    
    # Score metabólico composto
    metabolic_score = np.zeros(len(df_eng))
    
    if 'BMI' in df.columns:
        metabolic_score += np.where(df_eng['BMI'] >= 30, 2, np.where(df_eng['BMI'] >= 25, 1, 0))
    
    if 'glucose' in df.columns:
        metabolic_score += np.where(df_eng['glucose'] >= 126, 2, 
                                  np.where(df_eng['glucose'] >= 100, 1, 0))
    
    df_eng['score_metabolico'] = metabolic_score
    created_features.append('score_metabolico')
    
    # 7. Features polinomiais selecionadas
    print("   📈 Criando features polinomiais...")
    
    important_numerical_features = ['age', 'sysBP', 'diaBP', 'BMI', 'totChol']
    available_features = [f for f in important_numerical_features if f in df_eng.columns]
    
    for feature in available_features[:3]:  # Limitar para não explodir
        df_eng[f'{feature}_squared'] = df_eng[feature] ** 2
        df_eng[f'{feature}_sqrt'] = np.sqrt(np.abs(df_eng[feature]))
        created_features.extend([f'{feature}_squared', f'{feature}_sqrt'])
    
    print(f"   ✅ Criadas {len(created_features)} novas features médicas")
    
    return df_eng


def classify_blood_pressure_aha(systolic, diastolic):
    """Classificar pressão arterial segundo AHA/ACC 2017"""
    
    if systolic < 120 and diastolic < 80:
        return 0  # normal
    elif systolic < 130 and diastolic < 80:
        return 1  # elevada
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        return 2  # hipertensão estágio 1
    elif systolic >= 140 or diastolic >= 90:
        return 3  # hipertensão estágio 2
    elif systolic >= 180 or diastolic >= 120:
        return 4  # crise hipertensiva
    else:
        return 0  # indefinido -> normal


def select_relevant_features(df, target_col, threshold=0.05):
    """Selecionar features relevantes baseadas em correlação"""
    
    # Correlações com target (apenas numéricas)
    numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numerical_features:
        numerical_features.remove(target_col)
    
    correlations = df[numerical_features + [target_col]].corr()[target_col].abs()
    relevant_features = correlations[correlations >= threshold].index.tolist()
    
    if target_col in relevant_features:
        relevant_features.remove(target_col)
    
    # Adicionar features médicas importantes mesmo se correlação baixa
    medical_priority = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['pressure', 'pressao', 'age', 'idade', 
                                                      'bmi', 'framingham', 'score', 'map', 'pa']):
            if col not in relevant_features and col != target_col:
                medical_priority.append(col)
    
    final_features = list(set(relevant_features + medical_priority))
    
    return final_features


def generate_feature_engineering_report(df_original, df_engineered, new_features, correlations):
    """Gerar relatório do feature engineering"""
    
    report = {
        'original_features': df_original.shape[1],
        'engineered_features': df_engineered.shape[1],
        'created_features': len(new_features),
        'new_features_list': new_features,
        'feature_categories': {
            'blood_pressure': len([f for f in new_features if any(kw in f.lower() for kw in ['pa', 'pressure', 'pressao', 'map'])]),
            'cardiovascular_risk': len([f for f in new_features if any(kw in f.lower() for kw in ['risco', 'risk', 'score', 'framingham'])]),
            'interactions': len([f for f in new_features if any(kw in f.lower() for kw in ['interacao', 'razao', 'interaction'])]),
            'polynomials': len([f for f in new_features if any(kw in f.lower() for kw in ['squared', 'sqrt'])]),
            'categories': len([f for f in new_features if any(kw in f.lower() for kw in ['categoria', 'faixa'])])
        },
        'top_correlations': correlations.head(10).to_dict() if correlations is not None else {},
        'timestamp': datetime.now().isoformat()
    }
    
    return report


def save_results(df_final, report):
    """Salvar resultados do feature engineering"""
    
    save_path = Path('results/feature_engineering')
    save_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salvar dataset
    df_final.to_csv(save_path / f'medical_features_final_{timestamp}.csv', index=False)
    
    # Salvar relatório JSON
    with open(save_path / f'feature_report_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # Salvar relatório texto
    report_content = f"""
RELATÓRIO DE FEATURE ENGINEERING MÉDICO AVANÇADO
===============================================

Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Metodologia: Baseada no projeto A1_A2
Versão: Simplificada sem dependências externas

RESUMO GERAL:
============
Features originais: {report['original_features']}
Features após engineering: {report['engineered_features']}
Novas features criadas: {report['created_features']}
Aumento percentual: {(report['created_features'] / report['original_features']) * 100:.1f}%

CATEGORIAS DE FEATURES CRIADAS:
==============================
"""
    
    for categoria, quantidade in report['feature_categories'].items():
        report_content += f"- {categoria.replace('_', ' ').title()}: {quantidade} features\n"
    
    report_content += f"""
NOVAS FEATURES CRIADAS:
======================
"""
    
    for i, feature in enumerate(report['new_features_list'], 1):
        report_content += f"{i:2d}. {feature}\n"
    
    if report['top_correlations']:
        report_content += f"""
TOP CORRELAÇÕES COM TARGET:
==========================
"""
        for i, (feature, corr) in enumerate(report['top_correlations'].items(), 1):
            report_content += f"{i:2d}. {feature}: {corr:.4f}\n"
    
    report_content += f"""
METODOLOGIA MÉDICA APLICADA:
===========================
✅ Features de Pressão Arterial Avançadas:
   - MAP (Mean Arterial Pressure) calculada
   - Pressão de pulso e índices derivados
   - Categorização AHA/ACC 2017
   - Detecção de hipertensão sistólica isolada

✅ Features de Risco Cardiovascular:
   - Estratificação por faixas etárias
   - Scores de risco metabólico
   - Categorização de BMI médica

✅ Features de Interação Clínica:
   - Razões clinicamente relevantes
   - Interações idade-pressão arterial
   - Interações BMI-pressão arterial

✅ Scores Compostos Médicos:
   - Score de Framingham simplificado
   - Score metabólico composto
   - Features polinomiais selecionadas

BENEFÍCIOS ALCANÇADOS:
=====================
✅ Aplicação de conhecimento médico especializado
✅ Features baseadas em diretrizes clínicas
✅ Expansão inteligente do espaço de features
✅ Seleção automática de features relevantes
✅ Preparação para modelos de alta performance

ARQUIVOS GERADOS:
================
- medical_features_final_{timestamp}.csv
- feature_report_{timestamp}.json  
- feature_summary_{timestamp}.txt

===============================================
Sistema TCC Hipertensão ML v3.0 - Feature Engineering
===============================================
"""
    
    with open(save_path / f'feature_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n💾 Arquivos salvos:")
    print(f"   📄 medical_features_final_{timestamp}.csv")
    print(f"   📄 feature_report_{timestamp}.json")
    print(f"   📄 feature_summary_{timestamp}.txt")
    
    return save_path


if __name__ == "__main__":
    df_final, report = run_medical_feature_engineering_simple()