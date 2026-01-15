"""
Módulo de Validação Clínica
Baseado nas diretrizes AHA/ACC 2017 para Hipertensão
Inspirado na estrutura do projeto A1_A2
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import roc_curve, precision_recall_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class ClinicalValidator:
    """
    Validador clínico especializado para modelos de predição de hipertensão.
    Implementa validação baseada em conhecimento médico estabelecido.
    """
    
    def __init__(self):
        self.medical_guidelines = self._load_medical_guidelines()
        self.validation_results = {}
        
    def _load_medical_guidelines(self):
        """Carregar diretrizes médicas AHA/ACC 2017"""
        return {
            'blood_pressure_categories': {
                'normal': {'systolic': '<120', 'diastolic': '<80'},
                'elevated': {'systolic': '120-129', 'diastolic': '<80'},
                'stage1': {'systolic': '130-139', 'diastolic': '80-89'},
                'stage2': {'systolic': '≥140', 'diastolic': '≥90'},
                'crisis': {'systolic': '>180', 'diastolic': '>120'}
            },
            'risk_factors': {
                'age': {'men': '>55', 'women': '>65'},
                'diabetes': 'presence',
                'smoking': 'current_or_recent',
                'bmi': '>30',
                'cholesterol': '>240'
            },
            'clinical_thresholds': {
                'screening': {'sensitivity': '>90%', 'threshold': 'low'},
                'diagnosis': {'balanced': 'optimal', 'threshold': 'medium'},
                'confirmation': {'specificity': '>95%', 'threshold': 'high'}
            }
        }
    
    def validate_against_medical_knowledge(self, df, model_predictions, feature_importance):
        """
        Validar predições do modelo contra conhecimento médico estabelecido.
        
        Args:
            df: DataFrame com dados dos pacientes
            model_predictions: Predições do modelo
            feature_importance: Importância das features
            
        Returns:
            dict: Resultados da validação médica
        """
        print("🔍 Iniciando validação contra conhecimento médico...")
        
        validation = {
            'timestamp': datetime.now().isoformat(),
            'medical_consistency': {},
            'feature_validation': {},
            'clinical_logic': {},
            'risk_stratification': {}
        }
        
        # 1. Validar consistência das features médicas
        validation['feature_validation'] = self._validate_medical_features(
            df, feature_importance
        )
        
        # 2. Validar lógica clínica das predições
        validation['clinical_logic'] = self._validate_clinical_logic(
            df, model_predictions
        )
        
        # 3. Validar estratificação de risco
        validation['risk_stratification'] = self._validate_risk_stratification(
            df, model_predictions
        )
        
        # 4. Score geral de consistência médica
        validation['medical_consistency'] = self._calculate_medical_consistency_score(
            validation
        )
        
        self.validation_results = validation
        print("✅ Validação médica concluída!")
        
        return validation
    
    def _validate_medical_features(self, df, feature_importance):
        """Validar se features importantes fazem sentido médico"""
        medical_features_priority = {
            'pressao_sistolica': 'high',
            'pressao_diastolica': 'high', 
            'pressao_arterial_media': 'high',
            'idade': 'high',
            'imc': 'medium',
            'diabetes': 'high',
            'colesterol_total': 'medium',
            'fumante': 'medium'
        }
        
        validation = {
            'expected_vs_actual': {},
            'medical_logic_score': 0,
            'unexpected_features': [],
            'missing_important_features': []
        }
        
        # Verificar se features médicas importantes estão no topo
        if hasattr(feature_importance, 'index'):
            top_features = feature_importance.head(10).index.tolist()
        else:
            top_features = list(feature_importance.keys())[:10] if isinstance(feature_importance, dict) else []
        
        medical_score = 0
        total_medical_features = 0
        
        for feature, expected_priority in medical_features_priority.items():
            # Buscar features que contenham a palavra-chave
            matching_features = [f for f in top_features if feature.lower() in f.lower()]
            
            if matching_features:
                if expected_priority == 'high':
                    medical_score += 3
                elif expected_priority == 'medium':
                    medical_score += 2
                else:
                    medical_score += 1
            else:
                validation['missing_important_features'].append(feature)
            
            total_medical_features += 3 if expected_priority == 'high' else (2 if expected_priority == 'medium' else 1)
        
        validation['medical_logic_score'] = medical_score / total_medical_features if total_medical_features > 0 else 0
        validation['top_features_found'] = top_features
        
        return validation
    
    def _validate_clinical_logic(self, df, predictions):
        """Validar se predições seguem lógica clínica"""
        logic_validation = {
            'age_correlation': 0,
            'bp_correlation': 0,
            'diabetes_correlation': 0,
            'overall_logic_score': 0
        }
        
        try:
            # Validar correlação com idade
            if 'idade' in df.columns:
                age_high_risk_correlation = np.corrcoef(df['idade'], predictions)[0, 1]
                logic_validation['age_correlation'] = max(0, age_high_risk_correlation)
            
            # Validar correlação com pressão arterial
            bp_cols = [col for col in df.columns if 'pressao' in col.lower()]
            if bp_cols:
                bp_correlation = np.corrcoef(df[bp_cols[0]], predictions)[0, 1]
                logic_validation['bp_correlation'] = max(0, bp_correlation)
            
            # Validar correlação com diabetes
            if 'diabetes' in df.columns:
                diabetes_correlation = np.corrcoef(df['diabetes'], predictions)[0, 1]
                logic_validation['diabetes_correlation'] = max(0, diabetes_correlation)
            
            # Score geral de lógica
            scores = [v for v in logic_validation.values() if isinstance(v, (int, float)) and v != 0]
            logic_validation['overall_logic_score'] = np.mean(scores) if scores else 0
            
        except Exception as e:
            print(f"⚠️ Erro na validação de lógica clínica: {e}")
            logic_validation['error'] = str(e)
        
        return logic_validation
    
    def _validate_risk_stratification(self, df, predictions):
        """Validar estratificação de risco clínico"""
        stratification = {
            'low_risk_group': {},
            'medium_risk_group': {},
            'high_risk_group': {},
            'stratification_quality': 0
        }
        
        try:
            # Definir grupos baseado em probabilidades
            low_risk = predictions <= 0.3
            medium_risk = (predictions > 0.3) & (predictions <= 0.7)
            high_risk = predictions > 0.7
            
            # Analisar características de cada grupo
            for group_name, mask in [('low_risk_group', low_risk), 
                                   ('medium_risk_group', medium_risk),
                                   ('high_risk_group', high_risk)]:
                
                if mask.sum() > 0:
                    group_data = df[mask]
                    
                    stratification[group_name] = {
                        'count': int(mask.sum()),
                        'percentage': float(mask.sum() / len(df) * 100),
                        'avg_age': float(group_data['idade'].mean()) if 'idade' in df.columns else None,
                        'avg_systolic': float(group_data['pressao_sistolica'].mean()) if 'pressao_sistolica' in df.columns else None
                    }
            
            # Calcular qualidade da estratificação
            # Grupos devem ter diferenças significativas nas características
            if stratification['low_risk_group'].get('avg_age') and stratification['high_risk_group'].get('avg_age'):
                age_diff = stratification['high_risk_group']['avg_age'] - stratification['low_risk_group']['avg_age']
                stratification['stratification_quality'] = min(1.0, age_diff / 20)  # Normalizar por 20 anos
                
        except Exception as e:
            print(f"⚠️ Erro na validação de estratificação: {e}")
            stratification['error'] = str(e)
        
        return stratification
    
    def _calculate_medical_consistency_score(self, validation):
        """Calcular score geral de consistência médica"""
        scores = []
        
        # Score de features médicas
        if 'medical_logic_score' in validation['feature_validation']:
            scores.append(validation['feature_validation']['medical_logic_score'])
        
        # Score de lógica clínica
        if 'overall_logic_score' in validation['clinical_logic']:
            scores.append(validation['clinical_logic']['overall_logic_score'])
        
        # Score de estratificação
        if 'stratification_quality' in validation['risk_stratification']:
            scores.append(validation['risk_stratification']['stratification_quality'])
        
        overall_score = np.mean(scores) if scores else 0
        
        return {
            'overall_consistency_score': overall_score,
            'individual_scores': scores,
            'interpretation': self._interpret_consistency_score(overall_score)
        }
    
    def _interpret_consistency_score(self, score):
        """Interpretar score de consistência médica"""
        if score >= 0.8:
            return "Excelente consistência com conhecimento médico"
        elif score >= 0.6:
            return "Boa consistência médica"
        elif score >= 0.4:
            return "Consistência médica moderada"
        else:
            return "Baixa consistência médica - revisão necessária"
    
    def generate_medical_validation_report(self, save_path=None):
        """Gerar relatório de validação médica"""
        if not self.validation_results:
            print("❌ Nenhuma validação executada ainda")
            return None
        
        report = {
            'title': 'Relatório de Validação Médica',
            'timestamp': datetime.now().isoformat(),
            'validation_results': self.validation_results,
            'recommendations': self._generate_recommendations()
        }
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            
            with open(save_path / 'medical_validation_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📋 Relatório salvo em: {save_path / 'medical_validation_report.json'}")
        
        return report
    
    def _generate_recommendations(self):
        """Gerar recomendações baseadas na validação"""
        recommendations = []
        
        if not self.validation_results:
            return recommendations
        
        # Recomendações baseadas no score de consistência
        consistency_score = self.validation_results['medical_consistency']['overall_consistency_score']
        
        if consistency_score < 0.6:
            recommendations.append("Revisar feature engineering para melhor alinhamento médico")
            recommendations.append("Consultar especialistas médicos para validação")
        
        if self.validation_results['feature_validation'].get('missing_important_features'):
            recommendations.append("Considerar adicionar features médicas importantes não detectadas")
        
        recommendations.append("Validar com dados externos de diferentes populações")
        recommendations.append("Implementar monitoramento contínuo de consistência médica")
        
        return recommendations