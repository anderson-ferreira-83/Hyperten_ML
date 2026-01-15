"""
Feature Engineering Médica Avançada
Baseado na metodologia do projeto A1_A2 para criação de features médicas especializadas
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')


class MedicalFeatureEngineer:
    """
    Engenheiro de features médicas avançado baseado no conhecimento clínico.
    Implementa metodologia similar ao projeto A1_A2.
    """
    
    def __init__(self):
        self.medical_knowledge = self._load_medical_knowledge()
        self.feature_transformers = {}
        self.created_features = []
        
    def _load_medical_knowledge(self):
        """Carregar conhecimento médico para feature engineering"""
        
        return {
            'blood_pressure_categories': {
                'normal': {'systolic': (90, 120), 'diastolic': (60, 80)},
                'elevated': {'systolic': (120, 129), 'diastolic': (60, 80)},
                'stage1': {'systolic': (130, 139), 'diastolic': (80, 89)},
                'stage2': {'systolic': (140, 180), 'diastolic': (90, 120)},
                'crisis': {'systolic': (180, 250), 'diastolic': (120, 150)}
            },
            'cardiovascular_risk_factors': {
                'age_risk_thresholds': [45, 55, 65, 75],
                'bmi_categories': {
                    'underweight': (0, 18.5),
                    'normal': (18.5, 25.0),
                    'overweight': (25.0, 30.0),
                    'obese_1': (30.0, 35.0),
                    'obese_2': (35.0, 40.0),
                    'obese_3': (40.0, 60.0)
                },
                'cholesterol_risk': {
                    'total_chol_high': 240,
                    'ldl_high': 160,
                    'hdl_low_men': 40,
                    'hdl_low_women': 50,
                    'triglycerides_high': 200
                }
            },
            'physiological_formulas': {
                'map_formula': 'diastolic + (systolic - diastolic) / 3',
                'pulse_pressure': 'systolic - diastolic',
                'cardiovascular_risk_score': {
                    'age_weight': 0.3,
                    'bp_weight': 0.4,
                    'cholesterol_weight': 0.2,
                    'lifestyle_weight': 0.1
                }
            }
        }
    
    def engineer_comprehensive_features(self, df):
        """
        Criar features médicas abrangentes baseadas no conhecimento clínico.
        
        Args:
            df: DataFrame com dados médicos
            
        Returns:
            DataFrame com features engenheiradas
        """
        print("🧬 Iniciando feature engineering médico avançado...")
        
        df_engineered = df.copy()
        
        # 1. Features de pressão arterial avançadas
        df_engineered = self._create_blood_pressure_features(df_engineered)
        
        # 2. Features de risco cardiovascular
        df_engineered = self._create_cardiovascular_risk_features(df_engineered)
        
        # 3. Features de categorização médica
        df_engineered = self._create_medical_category_features(df_engineered)
        
        # 4. Features de interação médica
        df_engineered = self._create_medical_interaction_features(df_engineered)
        
        # 5. Features de score composto
        df_engineered = self._create_composite_risk_scores(df_engineered)
        
        # 6. Features polinomiais médicas
        df_engineered = self._create_polynomial_medical_features(df_engineered)
        
        # 7. Features de razões médicas
        df_engineered = self._create_medical_ratio_features(df_engineered)
        
        print(f"✅ Feature engineering concluído: {len(df_engineered.columns) - len(df.columns)} novas features")
        
        return df_engineered
    
    def _create_blood_pressure_features(self, df):
        """Criar features avançadas de pressão arterial"""
        
        print("   🩺 Criando features de pressão arterial...")
        
        # Identificar colunas de pressão arterial
        systolic_cols = [col for col in df.columns if 'sistolic' in col.lower() or 'sysbp' in col.lower()]
        diastolic_cols = [col for col in df.columns if 'diastolic' in col.lower() or 'diabp' in col.lower()]
        
        if systolic_cols and diastolic_cols:
            sys_col = systolic_cols[0]
            dia_col = diastolic_cols[0]
            
            # 1. Pressão arterial média (MAP)
            df[f'pressao_arterial_media_calculada'] = df[dia_col] + (df[sys_col] - df[dia_col]) / 3
            
            # 2. Pressão de pulso
            df[f'pressao_pulso'] = df[sys_col] - df[dia_col]
            
            # 3. Índice de pressão arterial (normalizado)
            df[f'indice_pressao_arterial'] = (df[sys_col] / 120 + df[dia_col] / 80) / 2
            
            # 4. Categoria de hipertensão AHA/ACC 2017
            df[f'categoria_hipertensao_aha'] = df.apply(
                lambda row: self._classify_blood_pressure_aha(row[sys_col], row[dia_col]), axis=1
            )
            
            # 5. Risco de pressão sistólica isolada
            df[f'hipertensao_sistolica_isolada'] = ((df[sys_col] >= 140) & (df[dia_col] < 90)).astype(int)
            
            # 6. Diferença da pressão normal
            df[f'desvio_pressao_normal_sys'] = df[sys_col] - 120
            df[f'desvio_pressao_normal_dia'] = df[dia_col] - 80
            
            # 7. Score de pressão arterial ponderado
            df[f'score_pressao_ponderado'] = (
                (df[sys_col] - 90) * 0.6 + (df[dia_col] - 60) * 0.4
            ) / 100
            
            self.created_features.extend([
                'pressao_arterial_media_calculada', 'pressao_pulso', 'indice_pressao_arterial',
                'categoria_hipertensao_aha', 'hipertensao_sistolica_isolada',
                'desvio_pressao_normal_sys', 'desvio_pressao_normal_dia', 'score_pressao_ponderado'
            ])
        
        return df
    
    def _create_cardiovascular_risk_features(self, df):
        """Criar features de risco cardiovascular"""
        
        print("   ❤️ Criando features de risco cardiovascular...")
        
        # Identificar colunas relevantes
        age_cols = [col for col in df.columns if 'age' in col.lower() or 'idade' in col.lower()]
        bmi_cols = [col for col in df.columns if 'bmi' in col.lower() or 'imc' in col.lower()]
        chol_cols = [col for col in df.columns if 'chol' in col.lower() or 'colesterol' in col.lower()]
        
        # 1. Features de idade
        if age_cols:
            age_col = age_cols[0]
            
            # Categorias de risco por idade
            df[f'faixa_etaria_risco'] = pd.cut(
                df[age_col], 
                bins=[0, 35, 45, 55, 65, 100], 
                labels=['baixo', 'moderado_baixo', 'moderado', 'alto', 'muito_alto']
            )
            
            # Score de idade normalizado
            df[f'score_idade_normalizado'] = (df[age_col] - 20) / 60  # Normalizar entre 20-80 anos
            
            # Risco exponencial por idade
            df[f'risco_exponencial_idade'] = np.exp((df[age_col] - 40) / 20)
            
            self.created_features.extend(['faixa_etaria_risco', 'score_idade_normalizado', 'risco_exponencial_idade'])
        
        # 2. Features de BMI
        if bmi_cols:
            bmi_col = bmi_cols[0]
            
            # Categoria de BMI
            df[f'categoria_bmi'] = df[bmi_col].apply(self._classify_bmi)
            
            # Distância do BMI normal
            df[f'desvio_bmi_normal'] = abs(df[bmi_col] - 22.5)  # 22.5 é o centro da faixa normal
            
            # Risco metabólico por BMI
            df[f'risco_metabolico_bmi'] = np.where(
                df[bmi_col] >= 30, 2,  # Obesidade = risco alto
                np.where(df[bmi_col] >= 25, 1, 0)  # Sobrepeso = risco moderado
            )
            
            self.created_features.extend(['categoria_bmi', 'desvio_bmi_normal', 'risco_metabolico_bmi'])
        
        # 3. Features de colesterol
        if chol_cols:
            chol_col = chol_cols[0]
            
            # Categoria de colesterol
            df[f'categoria_colesterol'] = pd.cut(
                df[chol_col],
                bins=[0, 200, 240, 500],
                labels=['normal', 'elevado', 'alto']
            )
            
            # Score de risco por colesterol
            df[f'score_risco_colesterol'] = (df[chol_col] - 150) / 100  # Normalizar
            
            self.created_features.extend(['categoria_colesterol', 'score_risco_colesterol'])
        
        return df
    
    def _create_medical_category_features(self, df):
        """Criar features categóricas médicas"""
        
        print("   📊 Criando features categóricas médicas...")
        
        # Identificar colunas para categorização
        systolic_cols = [col for col in df.columns if 'sistolic' in col.lower()]
        glucose_cols = [col for col in df.columns if 'glucose' in col.lower() or 'glicose' in col.lower()]
        
        # 1. Categoria de risco geral baseada em múltiplos fatores
        risk_factors = []
        
        if systolic_cols:
            sys_col = systolic_cols[0]
            risk_factors.append(df[sys_col] >= 140)  # Hipertensão
        
        if glucose_cols:
            gluc_col = glucose_cols[0]
            risk_factors.append(df[gluc_col] >= 126)  # Diabetes
        
        if risk_factors:
            df[f'numero_fatores_risco'] = sum(risk_factors)
            df[f'categoria_risco_multiplo'] = pd.cut(
                df[f'numero_fatores_risco'],
                bins=[-1, 0, 1, len(risk_factors)],
                labels=['baixo', 'moderado', 'alto']
            )
            
            self.created_features.extend(['numero_fatores_risco', 'categoria_risco_multiplo'])
        
        return df
    
    def _create_medical_interaction_features(self, df):
        """Criar features de interação médica"""
        
        print("   🔄 Criando features de interação médica...")
        
        # Identificar pares de features para interação
        important_features = []
        
        # Coletar features numéricas importantes
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['age', 'idade', 'pressure', 'pressao', 
                                                          'chol', 'bmi', 'imc', 'glucose', 'glicose']):
                if df[col].dtype in ['float64', 'int64']:
                    important_features.append(col)
        
        # Criar interações entre features importantes
        interactions_created = 0
        for i, feat1 in enumerate(important_features[:5]):  # Limitar para evitar explosão combinatória
            for feat2 in important_features[i+1:5]:
                
                # Interação multiplicativa
                df[f'interacao_{feat1}_{feat2}'] = df[feat1] * df[feat2]
                
                # Razão (se denominador não é zero)
                if (df[feat2] != 0).all():
                    df[f'razao_{feat1}_{feat2}'] = df[feat1] / df[feat2]
                
                interactions_created += 2
                self.created_features.extend([f'interacao_{feat1}_{feat2}', f'razao_{feat1}_{feat2}'])
                
                if interactions_created >= 10:  # Limitar número de interações
                    break
            if interactions_created >= 10:
                break
        
        return df
    
    def _create_composite_risk_scores(self, df):
        """Criar scores compostos de risco"""
        
        print("   🎯 Criando scores compostos de risco...")
        
        # 1. Score de Framingham simplificado
        framingham_components = []
        
        # Idade
        age_cols = [col for col in df.columns if 'age' in col.lower() or 'idade' in col.lower()]
        if age_cols:
            age_col = age_cols[0]
            age_score = np.where(df[age_col] >= 60, 2, np.where(df[age_col] >= 45, 1, 0))
            framingham_components.append(age_score)
        
        # Pressão sistólica
        systolic_cols = [col for col in df.columns if 'sistolic' in col.lower()]
        if systolic_cols:
            sys_col = systolic_cols[0]
            bp_score = np.where(df[sys_col] >= 160, 3, np.where(df[sys_col] >= 140, 2, 
                               np.where(df[sys_col] >= 130, 1, 0)))
            framingham_components.append(bp_score)
        
        # Colesterol
        chol_cols = [col for col in df.columns if 'chol' in col.lower()]
        if chol_cols:
            chol_col = chol_cols[0]
            chol_score = np.where(df[chol_col] >= 240, 2, np.where(df[chol_col] >= 200, 1, 0))
            framingham_components.append(chol_score)
        
        if framingham_components:
            df[f'score_framingham_simplificado'] = sum(framingham_components)
            self.created_features.append('score_framingham_simplificado')
        
        # 2. Score metabólico composto
        metabolic_components = []
        
        # BMI
        bmi_cols = [col for col in df.columns if 'bmi' in col.lower() or 'imc' in col.lower()]
        if bmi_cols:
            bmi_col = bmi_cols[0]
            bmi_score = np.where(df[bmi_col] >= 30, 2, np.where(df[bmi_col] >= 25, 1, 0))
            metabolic_components.append(bmi_score)
        
        # Glucose
        glucose_cols = [col for col in df.columns if 'glucose' in col.lower()]
        if glucose_cols:
            gluc_col = glucose_cols[0]
            gluc_score = np.where(df[gluc_col] >= 126, 2, np.where(df[gluc_col] >= 100, 1, 0))
            metabolic_components.append(gluc_score)
        
        if metabolic_components:
            df[f'score_metabolico_composto'] = sum(metabolic_components)
            self.created_features.append('score_metabolico_composto')
        
        return df
    
    def _create_polynomial_medical_features(self, df):
        """Criar features polinomiais médicas"""
        
        print("   📈 Criando features polinomiais médicas...")
        
        # Selecionar features médicas importantes para expansão polinomial
        medical_features = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['age', 'pressure', 'chol', 'bmi', 'glucose']) and \
               df[col].dtype in ['float64', 'int64'] and col in df.select_dtypes(include=[np.number]).columns:
                medical_features.append(col)
        
        if len(medical_features) >= 2:
            # Selecionar apenas as 3 features mais importantes
            medical_features = medical_features[:3]
            
            # Criar features polinomiais de grau 2
            for feature in medical_features:
                df[f'{feature}_squared'] = df[feature] ** 2
                df[f'{feature}_sqrt'] = np.sqrt(np.abs(df[feature]))
                
                self.created_features.extend([f'{feature}_squared', f'{feature}_sqrt'])
        
        return df
    
    def _create_medical_ratio_features(self, df):
        """Criar features de razões médicas"""
        
        print("   ➗ Criando features de razões médicas...")
        
        # Razões específicas baseadas no conhecimento médico
        
        # 1. Razão sistólica/diastólica
        systolic_cols = [col for col in df.columns if 'sistolic' in col.lower()]
        diastolic_cols = [col for col in df.columns if 'diastolic' in col.lower()]
        
        if systolic_cols and diastolic_cols:
            sys_col = systolic_cols[0]
            dia_col = diastolic_cols[0]
            
            df[f'razao_sistolica_diastolica'] = df[sys_col] / df[dia_col]
            self.created_features.append('razao_sistolica_diastolica')
        
        # 2. Razão idade/pressão (indicador de hipertensão precoce)
        age_cols = [col for col in df.columns if 'age' in col.lower() or 'idade' in col.lower()]
        if age_cols and systolic_cols:
            age_col = age_cols[0]
            sys_col = systolic_cols[0]
            
            df[f'razao_idade_pressao'] = df[age_col] / df[sys_col]
            self.created_features.append('razao_idade_pressao')
        
        # 3. Índice de risco cardiovascular composto
        if age_cols and systolic_cols:
            age_col = age_cols[0]
            sys_col = systolic_cols[0]
            
            df[f'indice_risco_cv_composto'] = (df[age_col] / 10) * (df[sys_col] / 100)
            self.created_features.append('indice_risco_cv_composto')
        
        return df
    
    def _classify_blood_pressure_aha(self, systolic, diastolic):
        """Classificar pressão arterial segundo AHA/ACC 2017"""
        
        if systolic < 120 and diastolic < 80:
            return 'normal'
        elif systolic < 130 and diastolic < 80:
            return 'elevada'
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            return 'hipertensao_estagio_1'
        elif systolic >= 140 or diastolic >= 90:
            return 'hipertensao_estagio_2'
        elif systolic >= 180 or diastolic >= 120:
            return 'crise_hipertensiva'
        else:
            return 'indefinido'
    
    def _classify_bmi(self, bmi):
        """Classificar BMI em categorias médicas"""
        
        if bmi < 18.5:
            return 'baixo_peso'
        elif 18.5 <= bmi < 25:
            return 'normal'
        elif 25 <= bmi < 30:
            return 'sobrepeso'
        elif 30 <= bmi < 35:
            return 'obesidade_1'
        elif 35 <= bmi < 40:
            return 'obesidade_2'
        else:
            return 'obesidade_3'
    
    def select_relevant_features(self, df, target_col, correlation_threshold=0.1):
        """Selecionar features relevantes baseadas em correlação e importância médica"""
        
        print(f"🎯 Selecionando features relevantes (threshold: {correlation_threshold})...")
        
        # Calcular correlações com target
        correlations = df.select_dtypes(include=[np.number]).corr()[target_col].abs()
        
        # Features acima do threshold de correlação
        relevant_features = correlations[correlations >= correlation_threshold].index.tolist()
        
        # Remover target da lista
        if target_col in relevant_features:
            relevant_features.remove(target_col)
        
        # Adicionar features médicas importantes mesmo se correlação baixa
        medical_priority_features = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['pressure', 'pressao', 'age', 'idade', 
                                                          'bmi', 'imc', 'framingham', 'score']):
                if col not in relevant_features and col != target_col:
                    medical_priority_features.append(col)
        
        # Combinar features
        final_features = list(set(relevant_features + medical_priority_features))
        
        print(f"✅ Selecionadas {len(final_features)} features relevantes")
        print(f"   📊 Por correlação: {len(relevant_features)}")
        print(f"   🏥 Prioridade médica: {len(medical_priority_features)}")
        
        return final_features
    
    def get_feature_engineering_report(self):
        """Gerar relatório do feature engineering"""
        
        report = {
            'total_features_created': len(self.created_features),
            'feature_categories': {
                'blood_pressure': len([f for f in self.created_features if 'pressao' in f or 'pressure' in f]),
                'cardiovascular_risk': len([f for f in self.created_features if any(keyword in f for keyword in ['risco', 'risk', 'score'])]),
                'interactions': len([f for f in self.created_features if 'interacao' in f or 'razao' in f]),
                'polynomials': len([f for f in self.created_features if 'squared' in f or 'sqrt' in f]),
                'categories': len([f for f in self.created_features if 'categoria' in f or 'faixa' in f])
            },
            'created_features': self.created_features,
            'medical_knowledge_applied': list(self.medical_knowledge.keys())
        }
        
        return report