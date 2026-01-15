"""
Módulo para feature engineering especializada em hipertensão.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from sklearn.feature_selection import (
    SelectKBest, f_classif, chi2, mutual_info_classif,
    RFE, SelectFromModel, VarianceThreshold
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

from ..utils.config import load_config
from ..utils.helpers import print_section


class MedicalFeatureEngineer:
    """
    Classe para feature engineering especializada baseada em conhecimento médico.
    """
    
    def __init__(self):
        """
        Inicializa o engenheiro de features médicas.
        """
        self.config = load_config()
        self.created_features = []
        self.medical_knowledge = self._load_medical_knowledge()
        
    def _load_medical_knowledge(self) -> Dict[str, any]:
        """
        Carrega conhecimento médico para criação de features.
        
        Returns:
            Dict com conhecimento médico estruturado
        """
        return {
            # Fórmulas médicas estabelecidas
            'blood_pressure': {
                'mean_arterial_pressure': 'Formula: (2*diastolic + systolic) / 3',
                'pulse_pressure': 'Formula: systolic - diastolic',
                'pressure_ratio': 'Formula: systolic / diastolic',
                'hypertension_stages': {
                    'normal': '< 120/80',
                    'elevated': '120-129/<80',
                    'stage1': '130-139/80-89',
                    'stage2': '≥140/≥90'
                }
            },
            'cardiovascular_risk': {
                'framingham_points': 'Age, sex, cholesterol, BP, smoking, diabetes',
                'metabolic_syndrome': 'Waist, BP, glucose, HDL, triglycerides',
                'risk_multipliers': 'Combined effect of multiple factors'
            },
            'anthropometric': {
                'bmi_categories': {
                    'underweight': '<18.5',
                    'normal': '18.5-24.9',
                    'overweight': '25-29.9',
                    'obese': '≥30'
                },
                'body_surface_area': 'Mosteller formula',
                'cardiac_index': 'Heart rate adjusted metrics'
            },
            'age_adjustments': {
                'age_bp_interaction': 'BP increases with age',
                'age_risk_exponential': 'Cardiovascular risk increases exponentially',
                'decades_categorization': 'Risk stratification by decades'
            }
        }
    
    def create_blood_pressure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features derivadas de pressão arterial baseadas em conhecimento médico.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com novas features de pressão arterial
        """
        df_features = df.copy()
        
        print("🩺 Criando features de pressão arterial...")
        
        # 1. Pressão Arterial Média (PAM)
        # Fórmula: PAM = (2 * PD + PS) / 3
        df_features['pressao_arterial_media'] = (
            2 * df_features['pressao_diastolica'] + df_features['pressao_sistolica']
        ) / 3
        
        # 2. Pressão de Pulso
        # Diferença entre sistólica e diastólica
        df_features['pressao_pulso'] = (
            df_features['pressao_sistolica'] - df_features['pressao_diastolica']
        )
        
        # 3. Razão de Pressão
        # Indicador de rigidez arterial
        df_features['razao_pressao'] = (
            df_features['pressao_sistolica'] / df_features['pressao_diastolica']
        )
        
        # 4. Categorização de Hipertensão (AHA/ACC Guidelines)
        conditions_bp = [
            (df_features['pressao_sistolica'] < 120) & (df_features['pressao_diastolica'] < 80),
            (df_features['pressao_sistolica'].between(120, 129)) & (df_features['pressao_diastolica'] < 80),
            (df_features['pressao_sistolica'].between(130, 139)) | (df_features['pressao_diastolica'].between(80, 89)),
            (df_features['pressao_sistolica'] >= 140) | (df_features['pressao_diastolica'] >= 90)
        ]
        choices_bp = [0, 1, 2, 3]  # Normal, Elevada, Estágio 1, Estágio 2
        
        df_features['categoria_hipertensao'] = np.select(conditions_bp, choices_bp, default=3)
        
        # 5. Desvio da Pressão Normal
        # Distância da pressão ideal (120/80)
        df_features['desvio_pressao_ideal'] = np.sqrt(
            (df_features['pressao_sistolica'] - 120)**2 + 
            (df_features['pressao_diastolica'] - 80)**2
        )
        
        # 6. Carga Pressórica
        # Produto das pressões (indicador de sobrecarga cardiovascular)
        df_features['carga_pressorica'] = (
            df_features['pressao_sistolica'] * df_features['pressao_diastolica']
        )
        
        # Features criadas
        bp_features = [
            'pressao_arterial_media', 'pressao_pulso', 'razao_pressao',
            'categoria_hipertensao', 'desvio_pressao_ideal', 'carga_pressorica'
        ]
        self.created_features.extend(bp_features)
        
        print(f"  ✅ {len(bp_features)} features de pressão arterial criadas")
        return df_features
    
    def create_cardiovascular_risk_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de risco cardiovascular baseadas em guidelines médicos.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com features de risco cardiovascular
        """
        df_features = df.copy()
        
        print("❤️  Criando features de risco cardiovascular...")
        
        # 1. Score de Risco Framingham Simplificado
        risk_score = 0
        
        # Pontos por idade
        if 'idade' in df_features.columns:
            risk_score += np.where(df_features['idade'] >= 65, 5,
                                  np.where(df_features['idade'] >= 55, 3,
                                          np.where(df_features['idade'] >= 45, 2,
                                                  np.where(df_features['idade'] >= 35, 1, 0))))
        
        # Pontos por sexo masculino
        if 'sexo' in df_features.columns:
            risk_score += df_features['sexo'] * 1
        
        # Pontos por pressão arterial
        risk_score += np.where(df_features['pressao_sistolica'] >= 160, 4,
                              np.where(df_features['pressao_sistolica'] >= 140, 3,
                                      np.where(df_features['pressao_sistolica'] >= 120, 1, 0)))
        
        # Pontos por colesterol
        if 'colesterol_total' in df_features.columns:
            risk_score += np.where(df_features['colesterol_total'] >= 240, 2,
                                  np.where(df_features['colesterol_total'] >= 200, 1, 0))
        
        # Pontos por diabetes
        if 'diabetes' in df_features.columns:
            risk_score += df_features['diabetes'] * 3
        
        # Pontos por tabagismo
        if 'fumante_atualmente' in df_features.columns:
            risk_score += df_features['fumante_atualmente'] * 2
        
        df_features['score_framingham'] = risk_score
        
        # 2. Síndrome Metabólica Score
        metabolic_score = 0
        
        # Obesidade abdominal (aproximação com IMC)
        metabolic_score += (df_features['imc'] >= 30).astype(int)
        
        # Hipertensão
        metabolic_score += ((df_features['pressao_sistolica'] >= 130) | 
                           (df_features['pressao_diastolica'] >= 85)).astype(int)
        
        # Glicemia elevada
        if 'glicose' in df_features.columns:
            metabolic_score += (df_features['glicose'] >= 100).astype(int)
        
        # Dislipidemia (aproximação)
        if 'colesterol_total' in df_features.columns:
            metabolic_score += (df_features['colesterol_total'] >= 200).astype(int)
        
        df_features['score_sindrome_metabolica'] = metabolic_score
        
        # 3. Carga Alostática (stress fisiológico)
        # Combinação de múltiplos sistemas
        allostatic_load = 0
        
        # Sistema cardiovascular
        allostatic_load += (df_features['pressao_sistolica'] > 140).astype(int)
        allostatic_load += (df_features['pressao_diastolica'] > 90).astype(int)
        
        # Sistema metabólico
        allostatic_load += (df_features['imc'] > 30).astype(int)
        if 'glicose' in df_features.columns:
            allostatic_load += (df_features['glicose'] > 100).astype(int)
        
        # Sistema lipídico
        if 'colesterol_total' in df_features.columns:
            allostatic_load += (df_features['colesterol_total'] > 240).astype(int)
        
        df_features['carga_alostatica'] = allostatic_load
        
        # 4. Interação Idade-Pressão
        # Risco aumenta exponencialmente com idade + pressão
        df_features['idade_pressao_interacao'] = (
            df_features['idade'] * df_features['pressao_arterial_media'] / 1000
        )
        
        # 5. Risco Combinado Ponderado
        # Combinação não-linear de fatores
        weights = {'age': 0.3, 'bp': 0.4, 'bmi': 0.2, 'chol': 0.1}
        
        age_norm = (df_features['idade'] - 30) / 40  # Normalizar 30-70 para 0-1
        bp_norm = (df_features['pressao_arterial_media'] - 80) / 60  # Normalizar ~80-140
        bmi_norm = (df_features['imc'] - 18) / 22  # Normalizar ~18-40
        
        if 'colesterol_total' in df_features.columns:
            chol_norm = (df_features['colesterol_total'] - 150) / 150  # Normalizar ~150-300
        else:
            chol_norm = 0
            weights['chol'] = 0
            # Redistribuir peso
            weights = {k: v/(1-0.1) if k != 'chol' else 0 for k, v in weights.items()}
        
        df_features['risco_combinado'] = (
            weights['age'] * age_norm +
            weights['bp'] * bp_norm +
            weights['bmi'] * bmi_norm +
            weights['chol'] * chol_norm
        )
        
        # Features criadas
        cv_features = [
            'score_framingham', 'score_sindrome_metabolica', 'carga_alostatica',
            'idade_pressao_interacao', 'risco_combinado'
        ]
        self.created_features.extend(cv_features)
        
        print(f"  ✅ {len(cv_features)} features de risco cardiovascular criadas")
        return df_features
    
    def create_anthropometric_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features antropométricas e metabólicas.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com features antropométricas
        """
        df_features = df.copy()
        
        print("📐 Criando features antropométricas...")
        
        # 1. Categorias de IMC
        conditions_bmi = [
            df_features['imc'] < 18.5,
            df_features['imc'].between(18.5, 24.9),
            df_features['imc'].between(25.0, 29.9),
            df_features['imc'].between(30.0, 34.9),
            df_features['imc'].between(35.0, 39.9),
            df_features['imc'] >= 40.0
        ]
        choices_bmi = [0, 1, 2, 3, 4, 5]  # Baixo peso, Normal, Sobrepeso, Obesidade I, II, III
        
        df_features['categoria_imc'] = np.select(conditions_bmi, choices_bmi, default=1)
        
        # 2. Desvio do IMC ideal
        # Distância do IMC ideal (22.5)
        df_features['desvio_imc_ideal'] = abs(df_features['imc'] - 22.5)
        
        # 3. Área de Superfície Corporal (Fórmula de Mosteller aproximada)
        # BSA = sqrt((altura_cm * peso_kg) / 3600)
        # Aproximação: peso ≈ IMC * altura²
        # Assumindo altura média baseada no IMC
        altura_estimada = 170  # cm (aproximação)
        peso_estimado = df_features['imc'] * (altura_estimada/100)**2
        df_features['area_superficie_corporal'] = np.sqrt(
            (altura_estimada * peso_estimado) / 3600
        )
        
        # 4. Índice de Massa Corporal Ajustado por Idade
        # IMC tem diferentes interpretações por idade
        age_adjustment = 1 + (df_features['idade'] - 40) * 0.01  # Ajuste pequeno
        df_features['imc_ajustado_idade'] = df_features['imc'] * age_adjustment
        
        # 5. Razão Cintura-Quadril Estimada
        # Aproximação baseada em IMC e sexo
        if 'sexo' in df_features.columns:
            # Homens tendem a ter mais gordura abdominal
            whr_base = np.where(df_features['sexo'] == 1, 0.85, 0.75)  # Masculino vs Feminino
            imc_factor = (df_features['imc'] - 25) * 0.01  # Ajuste por IMC
            df_features['razao_cintura_quadril_estimada'] = whr_base + imc_factor
        else:
            df_features['razao_cintura_quadril_estimada'] = 0.8 + (df_features['imc'] - 25) * 0.01
        
        # Features criadas
        anthro_features = [
            'categoria_imc', 'desvio_imc_ideal', 'area_superficie_corporal',
            'imc_ajustado_idade', 'razao_cintura_quadril_estimada'
        ]
        self.created_features.extend(anthro_features)
        
        print(f"  ✅ {len(anthro_features)} features antropométricas criadas")
        return df_features
    
    def create_cardiac_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features cardíacas e hemodinâmicas.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame with cardiac features
        """
        df_features = df.copy()
        
        print("💓 Criando features cardíacas...")
        
        # 1. Índice de Frequência-Pressão (Rate-Pressure Product)
        # Indicador de demanda miocárdica de oxigênio
        df_features['produto_frequencia_pressao'] = (
            df_features['frequencia_cardiaca'] * df_features['pressao_sistolica']
        )
        
        # 2. Reserva Cronotrópica Estimada
        # Capacidade de aumentar frequência cardíaca
        fc_max_estimada = 220 - df_features['idade']
        df_features['reserva_cronotopica'] = fc_max_estimada - df_features['frequencia_cardiaca']
        
        # 3. Índice de Eficiência Cardíaca
        # Relação entre débito (aproximado) e pressão
        # Débito cardíaco ≈ FC * Volume sistólico (aproximado por pressão de pulso)
        debito_aproximado = df_features['frequencia_cardiaca'] * df_features['pressao_pulso']
        df_features['eficiencia_cardiaca'] = debito_aproximado / df_features['pressao_arterial_media']
        
        # 4. Categorias de Frequência Cardíaca
        conditions_hr = [
            df_features['frequencia_cardiaca'] < 60,   # Bradicardia
            df_features['frequencia_cardiaca'].between(60, 100),  # Normal
            df_features['frequencia_cardiaca'] > 100   # Taquicardia
        ]
        choices_hr = [0, 1, 2]
        
        df_features['categoria_frequencia_cardiaca'] = np.select(conditions_hr, choices_hr, default=1)
        
        # 5. Trabalho Cardíaco Estimado
        # Aproximação do trabalho que o coração precisa fazer
        df_features['trabalho_cardiaco'] = (
            df_features['pressao_arterial_media'] * 
            df_features['frequencia_cardiaca'] * 
            df_features['area_superficie_corporal']
        )
        
        # Features criadas
        cardiac_features = [
            'produto_frequencia_pressao', 'reserva_cronotopica', 'eficiencia_cardiaca',
            'categoria_frequencia_cardiaca', 'trabalho_cardiaco'
        ]
        self.created_features.extend(cardiac_features)
        
        print(f"  ✅ {len(cardiac_features)} features cardíacas criadas")
        return df_features
    
    def create_lifestyle_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features relacionadas ao estilo de vida e fatores de risco modificáveis.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com features de estilo de vida
        """
        df_features = df.copy()
        
        print("🚭 Criando features de estilo de vida...")
        
        # 1. Carga Tabágica Total
        if 'fumante_atualmente' in df_features.columns and 'cigarros_por_dia' in df_features.columns:
            # Assumindo que fumantes atuais fumam há pelo menos 10 anos
            anos_fumando = np.where(df_features['fumante_atualmente'] == 1, 
                                   np.maximum(df_features['idade'] - 18, 1), 0)
            df_features['carga_tabagica'] = (
                df_features['cigarros_por_dia'] * anos_fumando / 20  # Maços-ano
            )
        else:
            df_features['carga_tabagica'] = 0
        
        # 2. Score de Fatores de Risco Modificáveis
        modifiable_risk = 0
        
        # Tabagismo
        if 'fumante_atualmente' in df_features.columns:
            modifiable_risk += df_features['fumante_atualmente'] * 3
        
        # Obesidade
        modifiable_risk += (df_features['imc'] >= 30).astype(int) * 2
        
        # Sedentarismo (aproximação: FC em repouso muito baixa ou muito alta)
        fc_anormal = ((df_features['frequencia_cardiaca'] < 50) | 
                     (df_features['frequencia_cardiaca'] > 90)).astype(int)
        modifiable_risk += fc_anormal
        
        df_features['score_fatores_modificaveis'] = modifiable_risk
        
        # 3. Índice de Medicação
        if 'medicamento_pressao' in df_features.columns:
            df_features['uso_medicacao'] = df_features['medicamento_pressao']
        else:
            df_features['uso_medicacao'] = 0
        
        # 4. Comorbidades Totais
        comorbidities = 0
        
        if 'diabetes' in df_features.columns:
            comorbidities += df_features['diabetes']
        
        # Obesidade como comorbidade
        comorbidities += (df_features['imc'] >= 30).astype(int)
        
        # Dislipidemia
        if 'colesterol_total' in df_features.columns:
            comorbidities += (df_features['colesterol_total'] >= 240).astype(int)
        
        df_features['total_comorbidades'] = comorbidities
        
        # 5. Perfil de Risco Comportamental
        # Combinação de fatores comportamentais
        behavioral_risk = 0
        
        if 'fumante_atualmente' in df_features.columns:
            behavioral_risk += df_features['fumante_atualmente'] * 2
        
        # Sobrepeso/Obesidade
        behavioral_risk += (df_features['imc'] >= 25).astype(int)
        
        # Uso de medicação (indica condição prévia)
        behavioral_risk += df_features['uso_medicacao']
        
        df_features['perfil_risco_comportamental'] = behavioral_risk
        
        # Features criadas
        lifestyle_features = [
            'carga_tabagica', 'score_fatores_modificaveis', 'uso_medicacao',
            'total_comorbidades', 'perfil_risco_comportamental'
        ]
        self.created_features.extend(lifestyle_features)
        
        print(f"  ✅ {len(lifestyle_features)} features de estilo de vida criadas")
        return df_features
    
    def create_age_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de interação com idade.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com features de interação com idade
        """
        df_features = df.copy()
        
        print("👴 Criando features de interação com idade...")
        
        # 1. Categorias Etárias para Risco Cardiovascular
        conditions_age = [
            df_features['idade'] < 40,
            df_features['idade'].between(40, 49),
            df_features['idade'].between(50, 59),
            df_features['idade'].between(60, 69),
            df_features['idade'] >= 70
        ]
        choices_age = [0, 1, 2, 3, 4]  # Jovem, Meia-idade precoce, Meia-idade, Idoso jovem, Idoso
        
        df_features['categoria_idade'] = np.select(conditions_age, choices_age, default=2)
        
        # 2. Interação Idade-IMC
        # Obesidade é mais perigosa em idades mais avançadas
        df_features['idade_imc_interacao'] = (
            df_features['idade'] * df_features['imc'] / 100
        )
        
        # 3. Interação Idade-Colesterol
        if 'colesterol_total' in df_features.columns:
            df_features['idade_colesterol_interacao'] = (
                df_features['idade'] * df_features['colesterol_total'] / 1000
            )
        else:
            df_features['idade_colesterol_interacao'] = 0
        
        # 4. Risco Exponencial por Idade
        # Risco cardiovascular aumenta exponencialmente com idade
        df_features['risco_exponencial_idade'] = np.exp((df_features['idade'] - 40) / 10)
        
        # 5. Décadas de Vida
        # Estratificação por décadas
        df_features['decada_vida'] = (df_features['idade'] // 10) - 2  # 30s=1, 40s=2, etc.
        
        # 6. Interação Idade-Sexo
        if 'sexo' in df_features.columns:
            # Risco diferencial por sexo e idade
            # Mulheres têm proteção até menopausa (~50 anos)
            df_features['idade_sexo_interacao'] = np.where(
                df_features['sexo'] == 0,  # Feminino
                np.where(df_features['idade'] > 50, 
                        (df_features['idade'] - 50) * 2,  # Risco acelera pós-menopausa
                        0),  # Proteção pré-menopausa
                df_features['idade'] - 30  # Masculino: risco linear desde jovem
            )
        else:
            df_features['idade_sexo_interacao'] = df_features['idade'] - 30
        
        # Features criadas
        age_features = [
            'categoria_idade', 'idade_imc_interacao', 'idade_colesterol_interacao',
            'risco_exponencial_idade', 'decada_vida', 'idade_sexo_interacao'
        ]
        self.created_features.extend(age_features)
        
        print(f"  ✅ {len(age_features)} features de interação com idade criadas")
        return df_features
    
    def create_complex_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria interações complexas entre múltiplas variáveis.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com interações complexas
        """
        df_features = df.copy()
        
        print("🔗 Criando interações complexas...")
        
        # 1. Triple Interaction: Idade × Pressão × IMC
        df_features['tripla_interacao_principal'] = (
            df_features['idade'] * 
            df_features['pressao_arterial_media'] * 
            df_features['imc'] / 10000
        )
        
        # 2. Síndrome Metabólica Score Ponderado
        # Versão mais sofisticada do score de síndrome metabólica
        metabolic_weighted = 0
        
        # Obesidade (peso 2)
        metabolic_weighted += (df_features['imc'] >= 30).astype(int) * 2
        
        # Hipertensão (peso 3)
        metabolic_weighted += ((df_features['pressao_sistolica'] >= 130) | 
                              (df_features['pressao_diastolica'] >= 85)).astype(int) * 3
        
        # Dislipidemia (peso 1.5)
        if 'colesterol_total' in df_features.columns:
            metabolic_weighted += (df_features['colesterol_total'] >= 200).astype(int) * 1.5
        
        # Glicemia alterada (peso 2.5)
        if 'glicose' in df_features.columns:
            metabolic_weighted += (df_features['glicose'] >= 100).astype(int) * 2.5
        
        # Diabetes (peso 4)
        if 'diabetes' in df_features.columns:
            metabolic_weighted += df_features['diabetes'] * 4
        
        df_features['sindrome_metabolica_ponderada'] = metabolic_weighted
        
        # 3. Carga Cardiovascular Total
        # Combinação não-linear de múltiplos fatores
        cv_load = (
            df_features['pressao_arterial_media'] * 0.4 +
            df_features['frequencia_cardiaca'] * 0.2 +
            df_features['imc'] * 3 +
            df_features['idade'] * 1.5
        )
        
        if 'colesterol_total' in df_features.columns:
            cv_load += df_features['colesterol_total'] * 0.1
        
        df_features['carga_cardiovascular_total'] = cv_load
        
        # 4. Índice de Vulnerabilidade
        # Combinação de fatores de fragilidade
        vulnerability = 0
        
        # Idade avançada
        vulnerability += (df_features['idade'] >= 65).astype(int) * 2
        
        # Múltiplas comorbidades
        vulnerability += np.minimum(df_features['total_comorbidades'], 3)  # Cap em 3
        
        # Uso de medicação
        vulnerability += df_features['uso_medicacao']
        
        # Pressão muito alta
        vulnerability += (df_features['pressao_sistolica'] >= 160).astype(int)
        
        df_features['indice_vulnerabilidade'] = vulnerability
        
        # 5. Score de Proteção
        # Fatores que podem ser protetivos
        protection_score = 5  # Score base
        
        # IMC normal
        protection_score += (df_features['imc'].between(18.5, 24.9)).astype(int) * 2
        
        # Pressão normal
        protection_score += ((df_features['pressao_sistolica'] < 120) & 
                            (df_features['pressao_diastolica'] < 80)).astype(int) * 2
        
        # Não fumante
        if 'fumante_atualmente' in df_features.columns:
            protection_score += (df_features['fumante_atualmente'] == 0).astype(int) * 1
        
        # Jovem
        protection_score += (df_features['idade'] < 45).astype(int) * 1
        
        # Sexo feminino (antes dos 50)
        if 'sexo' in df_features.columns:
            female_young = ((df_features['sexo'] == 0) & (df_features['idade'] < 50)).astype(int)
            protection_score += female_young * 1
        
        df_features['score_protecao'] = protection_score
        
        # 6. Risco vs Proteção Balance
        df_features['balanco_risco_protecao'] = (
            df_features['sindrome_metabolica_ponderada'] - df_features['score_protecao']
        )
        
        # Features criadas
        complex_features = [
            'tripla_interacao_principal', 'sindrome_metabolica_ponderada', 
            'carga_cardiovascular_total', 'indice_vulnerabilidade',
            'score_protecao', 'balanco_risco_protecao'
        ]
        self.created_features.extend(complex_features)
        
        print(f"  ✅ {len(complex_features)} interações complexas criadas")
        return df_features
    
    def apply_medical_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todo o pipeline de feature engineering médico.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com todas as features médicas criadas
        """
        print_section("FEATURE ENGINEERING MÉDICO ESPECIALIZADO", "=", 100)
        
        print(f"📊 Dataset original: {df.shape}")
        print(f"🔬 Aplicando conhecimento médico especializado...")
        
        # Aplicar todas as transformações em sequência
        df_features = df.copy()
        
        # 1. Features de pressão arterial
        df_features = self.create_blood_pressure_features(df_features)
        
        # 2. Features de risco cardiovascular
        df_features = self.create_cardiovascular_risk_features(df_features)
        
        # 3. Features antropométricas
        df_features = self.create_anthropometric_features(df_features)
        
        # 4. Features cardíacas
        df_features = self.create_cardiac_features(df_features)
        
        # 5. Features de estilo de vida
        df_features = self.create_lifestyle_features(df_features)
        
        # 6. Interações com idade
        df_features = self.create_age_interaction_features(df_features)
        
        # 7. Interações complexas
        df_features = self.create_complex_interactions(df_features)
        
        print_section("RESUMO DO FEATURE ENGINEERING", "=", 80)
        print(f"📊 Dataset final: {df_features.shape}")
        print(f"🆕 Total de features criadas: {len(self.created_features)}")
        print(f"📈 Aumento de features: {df_features.shape[1] - df.shape[1]}")
        
        print(f"\\n🔬 FEATURES CRIADAS POR CATEGORIA:")
        categories = {
            'Pressão Arterial': 6,
            'Risco Cardiovascular': 5,
            'Antropométricas': 5,
            'Cardíacas': 5,
            'Estilo de Vida': 5,
            'Interações com Idade': 6,
            'Interações Complexas': 6
        }
        
        for category, count in categories.items():
            print(f"  • {category}: {count} features")
        
        print(f"\\n✅ FEATURE ENGINEERING MÉDICO CONCLUÍDO!")
        print("="*100)
        
        return df_features
    
    def get_feature_importance_medical(self, X: pd.DataFrame, y: pd.Series, 
                                     method: str = 'random_forest') -> pd.DataFrame:
        """
        Calcula importância das features usando conhecimento médico.
        
        Args:
            X: Features
            y: Target
            method: Método para calcular importância
            
        Returns:
            DataFrame com importância das features
        """
        print_section("ANÁLISE DE IMPORTÂNCIA DAS FEATURES MÉDICAS")
        
        if method == 'random_forest':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            importances = model.feature_importances_
        elif method == 'mutual_info':
            importances = mutual_info_classif(X, y, random_state=42)
        else:
            # F-score
            f_scores, _ = f_classif(X, y)
            importances = f_scores / f_scores.max()  # Normalizar
        
        # Criar DataFrame de importâncias
        importance_df = pd.DataFrame({
            'Feature': X.columns,
            'Importance': importances,
            'Is_Medical_Feature': [feat in self.created_features for feat in X.columns]
        }).sort_values('Importance', ascending=False)
        
        # Adicionar categoria médica
        medical_categories = {
            'pressao': 'Pressão Arterial',
            'arterial': 'Pressão Arterial',
            'pulso': 'Pressão Arterial',
            'categoria_hipertensao': 'Pressão Arterial',
            'carga_pressorica': 'Pressão Arterial',
            'framingham': 'Risco Cardiovascular',
            'sindrome': 'Risco Cardiovascular',
            'alostatica': 'Risco Cardiovascular',
            'risco_combinado': 'Risco Cardiovascular',
            'imc': 'Antropométrica',
            'categoria_imc': 'Antropométrica',
            'superficie': 'Antropométrica',
            'cintura': 'Antropométrica',
            'frequencia': 'Cardíaca',
            'cardiaca': 'Cardíaca',
            'produto': 'Cardíaca',
            'cronotopica': 'Cardíaca',
            'trabalho': 'Cardíaca',
            'tabagica': 'Estilo de Vida',
            'modificaveis': 'Estilo de Vida',
            'medicacao': 'Estilo de Vida',
            'comorbidades': 'Estilo de Vida',
            'comportamental': 'Estilo de Vida',
            'idade': 'Interação Idade',
            'decada': 'Interação Idade',
            'exponencial': 'Interação Idade',
            'tripla': 'Interação Complexa',
            'vulnerabilidade': 'Interação Complexa',
            'protecao': 'Interação Complexa',
            'cardiovascular_total': 'Interação Complexa'
        }
        
        def categorize_feature(feature_name):
            for keyword, category in medical_categories.items():
                if keyword in feature_name.lower():
                    return category
            return 'Original'
        
        importance_df['Medical_Category'] = importance_df['Feature'].apply(categorize_feature)
        
        # Estatísticas por categoria
        category_stats = importance_df.groupby('Medical_Category')['Importance'].agg([
            'mean', 'max', 'count'
        ]).round(4)
        
        print(f"📊 Top 10 Features mais importantes:")
        print(importance_df.head(10)[['Feature', 'Importance', 'Medical_Category']].to_string(index=False))
        
        print(f"\n📈 Estatísticas por categoria médica:")
        print(category_stats)
        
        # Análise de features médicas vs originais
        medical_importance = importance_df[importance_df['Is_Medical_Feature']]['Importance'].mean()
        original_importance = importance_df[~importance_df['Is_Medical_Feature']]['Importance'].mean()
        
        print(f"\n🔬 COMPARAÇÃO FEATURES MÉDICAS vs ORIGINAIS:")
        print(f"  Importância média - Features médicas: {medical_importance:.4f}")
        print(f"  Importância média - Features originais: {original_importance:.4f}")
        print(f"  Ganho relativo: {((medical_importance/original_importance - 1) * 100):+.1f}%")
        
        return importance_df


class FeatureSelector:
    """Classe para seleção inteligente de features."""
    
    def __init__(self):
        self.selected_features = []
        self.selection_history = []
    
    def select_features_comprehensive(self, X: pd.DataFrame, y: pd.Series, 
                                    max_features: int = 50) -> pd.DataFrame:
        """
        Seleção abrangente de features usando múltiplos métodos.
        
        Args:
            X: Features
            y: Target
            max_features: Número máximo de features
            
        Returns:
            DataFrame com features selecionadas
        """
        try:
            from ..utils.helpers import print_section
        except ImportError:
            def print_section(title, char="=", width=80):
                print(f"\n{char * width}")
                print(f" {title}")
                print(f"{char * width}")
        
        print_section("SELEÇÃO INTELIGENTE DE FEATURES", "=", 80)
        
        print(f"📊 Features iniciais: {X.shape[1]}")
        print(f"🎯 Meta de features: {max_features}")
        
        # 1. Remover features com baixa variância
        print("\n🔄 Removendo features com baixa variância...")
        from sklearn.feature_selection import VarianceThreshold
        variance_selector = VarianceThreshold(threshold=0.01)
        X_variance = pd.DataFrame(
            variance_selector.fit_transform(X),
            columns=X.columns[variance_selector.get_support()],
            index=X.index
        )
        print(f"  ✅ Removidas: {X.shape[1] - X_variance.shape[1]} features")
        
        # 2. Seleção univariada
        print("\n📈 Seleção univariada (F-score)...")
        from sklearn.feature_selection import SelectKBest, f_classif
        k_best = min(max_features * 2, X_variance.shape[1])
        univariate_selector = SelectKBest(score_func=f_classif, k=k_best)
        X_univariate = pd.DataFrame(
            univariate_selector.fit_transform(X_variance, y),
            columns=X_variance.columns[univariate_selector.get_support()],
            index=X_variance.index
        )
        print(f"  ✅ Selecionadas: {X_univariate.shape[1]} features")
        
        # 3. Seleção baseada em modelo (Random Forest)
        print("\n🌳 Seleção baseada em Random Forest...")
        from sklearn.feature_selection import SelectFromModel
        from sklearn.ensemble import RandomForestClassifier
        rf_selector = SelectFromModel(
            RandomForestClassifier(n_estimators=100, random_state=42),
            max_features=max_features
        )
        X_model_based = pd.DataFrame(
            rf_selector.fit_transform(X_univariate, y),
            columns=X_univariate.columns[rf_selector.get_support()],
            index=X_univariate.index
        )
        print(f"  ✅ Selecionadas: {X_model_based.shape[1]} features")
        
        # 4. RFE (Recursive Feature Elimination)
        if X_model_based.shape[1] > max_features:
            print("\n🔄 Aplicando RFE para refinamento final...")
            from sklearn.feature_selection import RFE
            from sklearn.linear_model import LogisticRegression
            rfe_selector = RFE(
                LogisticRegression(random_state=42, max_iter=1000),
                n_features_to_select=max_features
            )
            X_final = pd.DataFrame(
                rfe_selector.fit_transform(X_model_based, y),
                columns=X_model_based.columns[rfe_selector.get_support()],
                index=X_model_based.index
            )
            print(f"  ✅ Seleção final: {X_final.shape[1]} features")
        else:
            X_final = X_model_based
        
        # Salvar histórico
        self.selected_features = list(X_final.columns)
        self.selection_history = [
            ('Original', X.shape[1]),
            ('Pós-Variância', X_variance.shape[1]),
            ('Pós-Univariada', X_univariate.shape[1]),
            ('Pós-Random Forest', X_model_based.shape[1]),
            ('Final', X_final.shape[1])
        ]
        
        print(f"\n✅ SELEÇÃO CONCLUÍDA:")
        for step, count in self.selection_history:
            print(f"  {step}: {count} features")
        
        return X_final


def create_medical_feature_engineer() -> MedicalFeatureEngineer:
    """Função de conveniência para criar engenheiro de features médicas."""
    return MedicalFeatureEngineer()


def create_feature_selector() -> FeatureSelector:
    """Função de conveniência para criar seletor de features."""
    return FeatureSelector()


if __name__ == "__main__":
    print("🧪 Testando módulo MedicalFeatureEngineer...")
    
    # Criar dados de teste
    np.random.seed(42)
    n_samples = 1000
    
    test_data = pd.DataFrame({
        'idade': np.random.randint(30, 70, n_samples),
        'sexo': np.random.choice([0, 1], n_samples),
        'pressao_sistolica': np.random.normal(130, 20, n_samples),
        'pressao_diastolica': np.random.normal(85, 15, n_samples),
        'imc': np.random.normal(25, 5, n_samples),
        'colesterol_total': np.random.normal(220, 40, n_samples),
        'frequencia_cardiaca': np.random.normal(75, 12, n_samples),
        'glicose': np.random.normal(95, 20, n_samples),
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'fumante_atualmente': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'cigarros_por_dia': np.random.exponential(5, n_samples),
        'medicamento_pressao': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'risco_hipertensao': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    # Testar feature engineer
    engineer = MedicalFeatureEngineer()
    enhanced_data = engineer.apply_medical_feature_engineering(test_data)
    
    # Testar seletor
    selector = FeatureSelector()
    X = enhanced_data.drop('risco_hipertensao', axis=1)
    y = enhanced_data['risco_hipertensao']
    
    selected_features = selector.select_features_comprehensive(X, y, max_features=25)
    
    print(f"\n✅ Teste concluído!")
    print(f"📊 Features originais: {test_data.shape[1] - 1}")
    print(f"🔬 Features após engineering: {X.shape[1]}")
    print(f"🎯 Features selecionadas: {selected_features.shape[1]}")
    print(f"🏥 MedicalFeatureEngineer e FeatureSelector prontos para uso")