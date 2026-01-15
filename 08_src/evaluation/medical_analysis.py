"""
🏥 Módulo de Análise Médica Especializada para Hipertensão

Este módulo implementa análises médicas avançadas baseadas em diretrizes clínicas
para avaliação de risco cardiovascular e hipertensão.

Autores: Tiago Dias, Nicolas Vagnes, Marcelo Colpani e Rubens Collin
Instituição: CEUNSP - Salto
Curso: Faculdade de Ciência da Computação
"""

import pandas as pd
import numpy as np
from typing import Dict, Union, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from ..utils.helpers import print_section
except ImportError:
    def print_section(title: str, char: str = "=", width: int = 80) -> None:
        """Função fallback para print_section"""
        print(f"\n{char * width}")
        print(f" {title}")
        print(f"{char * width}")


class MedicalAnalyzer:
    """
    Classe para análises médicas especializadas em hipertensão e risco cardiovascular.
    
    Implementa análises baseadas em diretrizes médicas como:
    - Categorização de pressão arterial (AHA/ESC)
    - Avaliação de síndrome metabólica
    - Cálculo de risco cardiovascular
    - Análise de comorbidades
    """
    
    def __init__(self):
        """
        Inicializa o analisador médico com constantes e parâmetros médicos.
        """
        # Categorias de pressão arterial baseadas em diretrizes AHA/ESC
        self.bp_categories = {
            'Normal': {'systolic': (0, 120), 'diastolic': (0, 80)},
            'Elevada': {'systolic': (120, 130), 'diastolic': (0, 80)},
            'Hipertensão Estágio 1': {'systolic': (130, 140), 'diastolic': (80, 90)},
            'Hipertensão Estágio 2': {'systolic': (140, 180), 'diastolic': (90, 120)},
            'Crise Hipertensiva': {'systolic': (180, 300), 'diastolic': (120, 200)}
        }
        
        # Parâmetros para análise de risco cardiovascular
        self.cv_risk_params = {
            'age_thresholds': [35, 45, 55, 65],
            'bp_thresholds': [120, 130, 140, 160],
            'bmi_thresholds': [25, 30, 35],
            'cholesterol_thresholds': [200, 240]
        }
    
    def categorize_blood_pressure(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categoriza pressão arterial conforme diretrizes AHA/ESC.
        
        Args:
            df: DataFrame com dados de pressão arterial
            
        Returns:
            DataFrame com coluna adicional 'categoria_pa'
        """
        df_bp = df.copy()
        
        # Garantir que as colunas existem
        required_cols = ['pressao_sistolica', 'pressao_diastolica']
        missing_cols = [col for col in required_cols if col not in df_bp.columns]
        if missing_cols:
            raise ValueError(f"Colunas necessárias não encontradas: {missing_cols}")
        
        def classify_bp(row):
            sys_bp = row['pressao_sistolica']
            dia_bp = row['pressao_diastolica']
            
            # Verificar se há valores ausentes
            if pd.isna(sys_bp) or pd.isna(dia_bp):
                return 'Não Classificada'
            
            # Crise hipertensiva
            if sys_bp >= 180 or dia_bp >= 120:
                return 'Crise Hipertensiva'
            # Hipertensão Estágio 2
            elif sys_bp >= 140 or dia_bp >= 90:
                return 'Hipertensão Estágio 2'
            # Hipertensão Estágio 1
            elif sys_bp >= 130 or dia_bp >= 80:
                return 'Hipertensão Estágio 1'
            # Pressão elevada
            elif sys_bp >= 120 and dia_bp < 80:
                return 'Elevada'
            # Normal
            elif sys_bp < 120 and dia_bp < 80:
                return 'Normal'
            else:
                return 'Não Classificada'
        
        df_bp['categoria_pa'] = df_bp.apply(classify_bp, axis=1)
        
        return df_bp
    
    def categorize_cardiovascular_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score de risco cardiovascular baseado em múltiplos fatores.
        
        Args:
            df: DataFrame com dados dos pacientes
            
        Returns:
            DataFrame com score e categoria de risco cardiovascular
        """
        df_risk = df.copy()
        
        # Inicializar score de risco
        risk_score = pd.Series(0, index=df_risk.index)
        
        # Idade
        if 'idade' in df_risk.columns:
            risk_score += np.where(df_risk['idade'] >= 65, 4,
                                 np.where(df_risk['idade'] >= 55, 3,
                                        np.where(df_risk['idade'] >= 45, 2,
                                               np.where(df_risk['idade'] >= 35, 1, 0))))
        
        # Pressão sistólica
        if 'pressao_sistolica' in df_risk.columns:
            risk_score += np.where(df_risk['pressao_sistolica'] >= 160, 4,
                                 np.where(df_risk['pressao_sistolica'] >= 140, 3,
                                        np.where(df_risk['pressao_sistolica'] >= 130, 2,
                                               np.where(df_risk['pressao_sistolica'] >= 120, 1, 0))))
        
        # IMC
        if 'imc' in df_risk.columns:
            risk_score += np.where(df_risk['imc'] >= 35, 3,
                                 np.where(df_risk['imc'] >= 30, 2,
                                        np.where(df_risk['imc'] >= 25, 1, 0)))
        
        # Colesterol
        risk_score += np.where(df_risk['colesterol_total'] >= 240, 2,
                              np.where(df_risk['colesterol_total'] >= 200, 1, 0))
        
        # Diabetes
        if 'diabetes' in df_risk.columns:
            risk_score += df_risk['diabetes'] * 3
        
        # Tabagismo
        if 'fumante_atualmente' in df_risk.columns:
            risk_score += df_risk['fumante_atualmente'] * 2
        
        # Medicamento para pressão (indica hipertensão prévia)
        if 'medicamento_pressao' in df_risk.columns:
            risk_score += df_risk['medicamento_pressao'] * 2
        
        df_risk['score_risco_cv'] = risk_score
        
        # Categorizar risco
        df_risk['categoria_risco_cv'] = pd.cut(df_risk['score_risco_cv'],
                                              bins=[-1, 3, 6, 9, 20],
                                              labels=['Baixo', 'Moderado', 'Alto', 'Muito Alto'])
        
        return df_risk
    
    def analyze_metabolic_syndrome(self, df: pd.DataFrame) -> Dict[str, Union[int, float, pd.DataFrame]]:
        """
        Analisa critérios para síndrome metabólica.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            Dict com análise da síndrome metabólica
        """
        # Critérios para síndrome metabólica (simplificados)
        criteria = {
            'obesidade_abdominal': df['imc'] >= 30,  # Aproximação usando IMC
            'hipertensao': (df['pressao_sistolica'] >= 130) | (df['pressao_diastolica'] >= 85),
            'glicemia_elevada': df['glicose'] >= 100,
            'colesterol_baixo': df['colesterol_total'] >= 200  # Aproximação
        }
        
        # Medicamento para pressão indica hipertensão
        if 'medicamento_pressao' in df.columns:
            criteria['hipertensao'] = criteria['hipertensao'] | (df['medicamento_pressao'] == 1)
        
        # Diabetes indica glicemia alterada
        if 'diabetes' in df.columns:
            criteria['glicemia_elevada'] = criteria['glicemia_elevada'] | (df['diabetes'] == 1)
        
        # Contar critérios por paciente
        df_temp = df.copy()
        for criterion, condition in criteria.items():
            df_temp[criterion] = condition.astype(int)
        
        # Síndrome metabólica = 3 ou mais critérios
        criterion_cols = list(criteria.keys())
        df_temp['num_criterios'] = df_temp[criterion_cols].sum(axis=1)
        df_temp['sindrome_metabolica'] = df_temp['num_criterios'] >= 3
        
        # Análise estatística
        analysis = {
            'total_pacientes': len(df_temp),
            'com_sindrome_metabolica': df_temp['sindrome_metabolica'].sum(),
            'prevalencia_sindrome': (df_temp['sindrome_metabolica'].sum() / len(df_temp)) * 100,
            'media_criterios': df_temp['num_criterios'].mean(),
            'distribuicao_criterios': df_temp['num_criterios'].value_counts().sort_index(),
            'criterios_prevalencia': {criterion: condition.sum() / len(df) * 100 
                                    for criterion, condition in criteria.items()},
            'dados_detalhados': df_temp
        }
        
        return analysis
    
    def calculate_cardiovascular_risk_score(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> Dict[str, Union[float, pd.DataFrame]]:
        """
        Calcula score de risco cardiovascular detalhado.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Dict com análise de risco cardiovascular
        """
        df_risk = self.categorize_cardiovascular_risk(df)
        
        # Análise por categoria de risco
        risk_analysis = df_risk.groupby('categoria_risco_cv').agg({
            target_col: ['count', 'sum', 'mean'],
            'idade': 'mean',
            'pressao_sistolica': 'mean',
            'pressao_diastolica': 'mean',
            'imc': 'mean',
            'colesterol_total': 'mean'
        }).round(2)
        
        # Simplificar nomes das colunas
        risk_analysis.columns = ['total_pacientes', 'com_hipertensao', 'prevalencia_hipertensao',
                               'idade_media', 'pressao_sist_media', 'pressao_diast_media',
                               'imc_medio', 'colesterol_medio']
        
        # Converter prevalência para porcentagem
        risk_analysis['prevalencia_hipertensao'] *= 100
        
        # Estatísticas gerais
        stats = {
            'score_medio': df_risk['score_risco_cv'].mean(),
            'score_mediano': df_risk['score_risco_cv'].median(),
            'score_desvio': df_risk['score_risco_cv'].std(),
            'distribuicao_categorias': df_risk['categoria_risco_cv'].value_counts(),
            'analise_por_categoria': risk_analysis,
            'dados_completos': df_risk
        }
        
        return stats
    
    def analyze_comorbidities(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> Dict[str, Union[float, pd.DataFrame]]:
        """
        Analisa comorbidades e fatores associados.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Dict com análise de comorbidades
        """
        comorbidities = {}
        
        # Diabetes
        if 'diabetes' in df.columns:
            diabetes_analysis = {
                'prevalencia_geral': (df['diabetes'].sum() / len(df)) * 100,
                'prevalencia_hipertensao': (df[df[target_col] == 1]['diabetes'].sum() / 
                                          df[df[target_col] == 1].shape[0]) * 100 if df[df[target_col] == 1].shape[0] > 0 else 0,
                'risco_relativo': self._calculate_relative_risk(df, 'diabetes', target_col)
            }
            comorbidities['diabetes'] = diabetes_analysis
        
        # Tabagismo
        if 'fumante_atualmente' in df.columns:
            smoking_analysis = {
                'prevalencia_geral': (df['fumante_atualmente'].sum() / len(df)) * 100,
                'prevalencia_hipertensao': (df[df[target_col] == 1]['fumante_atualmente'].sum() / 
                                           df[df[target_col] == 1].shape[0]) * 100 if df[df[target_col] == 1].shape[0] > 0 else 0,
                'risco_relativo': self._calculate_relative_risk(df, 'fumante_atualmente', target_col)
            }
            comorbidities['tabagismo'] = smoking_analysis
        
        # Obesidade (IMC >= 30)
        df_temp = df.copy()
        df_temp['obesidade'] = (df_temp['imc'] >= 30).astype(int)
        obesity_analysis = {
            'prevalencia_geral': (df_temp['obesidade'].sum() / len(df_temp)) * 100,
            'prevalencia_hipertensao': (df_temp[df_temp[target_col] == 1]['obesidade'].sum() / 
                                       df_temp[df_temp[target_col] == 1].shape[0]) * 100 if df_temp[df_temp[target_col] == 1].shape[0] > 0 else 0,
            'risco_relativo': self._calculate_relative_risk(df_temp, 'obesidade', target_col)
        }
        comorbidities['obesidade'] = obesity_analysis
        
        # Colesterol alto (>= 240)
        df_temp['colesterol_alto'] = (df_temp['colesterol_total'] >= 240).astype(int)
        cholesterol_analysis = {
            'prevalencia_geral': (df_temp['colesterol_alto'].sum() / len(df_temp)) * 100,
            'prevalencia_hipertensao': (df_temp[df_temp[target_col] == 1]['colesterol_alto'].sum() / 
                                       df_temp[df_temp[target_col] == 1].shape[0]) * 100 if df_temp[df_temp[target_col] == 1].shape[0] > 0 else 0,
            'risco_relativo': self._calculate_relative_risk(df_temp, 'colesterol_alto', target_col)
        }
        comorbidities['colesterol_alto'] = cholesterol_analysis
        
        return comorbidities
    
    def _calculate_relative_risk(self, df: pd.DataFrame, exposure: str, outcome: str) -> float:
        """
        Calcula risco relativo.
        
        Args:
            df: DataFrame com dados
            exposure: Variável de exposição
            outcome: Variável de desfecho
            
        Returns:
            Risco relativo
        """
        # Tabela 2x2
        exposed_with_outcome = df[(df[exposure] == 1) & (df[outcome] == 1)].shape[0]
        exposed_without_outcome = df[(df[exposure] == 1) & (df[outcome] == 0)].shape[0]
        unexposed_with_outcome = df[(df[exposure] == 0) & (df[outcome] == 1)].shape[0]
        unexposed_without_outcome = df[(df[exposure] == 0) & (df[outcome] == 0)].shape[0]
        
        # Calcular riscos
        risk_exposed = exposed_with_outcome / (exposed_with_outcome + exposed_without_outcome) if (exposed_with_outcome + exposed_without_outcome) > 0 else 0
        risk_unexposed = unexposed_with_outcome / (unexposed_with_outcome + unexposed_without_outcome) if (unexposed_with_outcome + unexposed_without_outcome) > 0 else 0
        
        # Risco relativo
        relative_risk = risk_exposed / risk_unexposed if risk_unexposed > 0 else np.inf
        
        return relative_risk
    
    def create_medical_report(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> Dict[str, any]:
        """
        Cria relatório médico completo.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Dict com relatório médico completo
        """
        print_section("RELATÓRIO MÉDICO COMPLETO - ANÁLISE DE HIPERTENSÃO", "=", 100)
        
        report = {
            'dados_gerais': self._analyze_general_data(df, target_col),
            'categorias_pressao': self._analyze_blood_pressure_categories(df, target_col),
            'sindrome_metabolica': self.analyze_metabolic_syndrome(df),
            'risco_cardiovascular': self.calculate_cardiovascular_risk_score(df, target_col),
            'comorbidades': self.analyze_comorbidities(df, target_col),
            'analise_demografica': self._analyze_demographics(df, target_col)
        }
        
        # Imprimir resumo executivo
        self._print_executive_summary(report)
        
        return report
    
    def _analyze_general_data(self, df: pd.DataFrame, target_col: str) -> Dict[str, any]:
        """
        Analisa dados gerais da população.
        """
        return {
            'total_pacientes': len(df),
            'prevalencia_hipertensao': (df[target_col].sum() / len(df)) * 100,
            'idade_media': df['idade'].mean(),
            'idade_mediana': df['idade'].median(),
            'pressao_sistolica_media': df['pressao_sistolica'].mean(),
            'pressao_diastolica_media': df['pressao_diastolica'].mean(),
            'imc_medio': df['imc'].mean(),
            'colesterol_medio': df['colesterol_total'].mean()
        }
    
    def _analyze_blood_pressure_categories(self, df: pd.DataFrame, target_col: str) -> Dict[str, any]:
        """
        Analisa categorias de pressão arterial.
        """
        df_bp = self.categorize_blood_pressure(df)
        
        bp_analysis = df_bp.groupby('categoria_pa')[target_col].agg(['count', 'sum', 'mean']).reset_index()
        bp_analysis.columns = ['categoria', 'total', 'com_hipertensao', 'prevalencia']
        bp_analysis['prevalencia'] *= 100
        
        return {
            'distribuicao_categorias': df_bp['categoria_pa'].value_counts(),
            'analise_detalhada': bp_analysis
        }
    
    def _analyze_demographics(self, df: pd.DataFrame, target_col: str) -> Dict[str, any]:
        """
        Analisa dados demográficos.
        """
        demographics = {}
        
        # Análise por sexo
        if 'sexo' in df.columns:
            sex_analysis = df.groupby('sexo')[target_col].agg(['count', 'sum', 'mean']).reset_index()
            sex_analysis.columns = ['sexo', 'total', 'com_hipertensao', 'prevalencia']
            sex_analysis['prevalencia'] *= 100
            sex_analysis['sexo'] = sex_analysis['sexo'].map({0: 'Feminino', 1: 'Masculino'})
            demographics['por_sexo'] = sex_analysis
        
        # Análise por faixa etária
        df_temp = df.copy()
        df_temp['faixa_etaria'] = pd.cut(df_temp['idade'],
                                        bins=[30, 40, 50, 60, 70],
                                        labels=['30-40', '40-50', '50-60', '60-70'])
        
        age_analysis = df_temp.groupby('faixa_etaria')[target_col].agg(['count', 'sum', 'mean']).reset_index()
        age_analysis.columns = ['faixa_etaria', 'total', 'com_hipertensao', 'prevalencia']
        age_analysis['prevalencia'] *= 100
        demographics['por_idade'] = age_analysis
        
        return demographics
    
    def _print_executive_summary(self, report: Dict[str, any]):
        """
        Imprime resumo executivo do relatório.
        """
        dados = report['dados_gerais']
        sindrome = report['sindrome_metabolica']
        comorbidades = report['comorbidades']
        
        print("\n🏥 RESUMO EXECUTIVO")
        print("="*50)
        print(f"👥 População estudada: {dados['total_pacientes']:,} pacientes")
        print(f"📊 Prevalência de hipertensão: {dados['prevalencia_hipertensao']:.1f}%")
        print(f"👤 Idade média: {dados['idade_media']:.1f} anos")
        print(f"🩺 Pressão arterial média: {dados['pressao_sistolica_media']:.0f}/{dados['pressao_diastolica_media']:.0f} mmHg")
        print(f"⚖️ IMC médio: {dados['imc_medio']:.1f} kg/m²")
        
        print(f"\n🔬 SÍNDROME METABÓLICA")
        print(f"📈 Prevalência: {sindrome['prevalencia_sindrome']:.1f}%")
        print(f"📊 Média de critérios: {sindrome['media_criterios']:.1f}")
        
        print(f"\n🏥 PRINCIPAIS COMORBIDADES")
        for nome, dados_comorb in comorbidades.items():
            print(f"  • {nome.title()}: {dados_comorb['prevalencia_geral']:.1f}% (RR: {dados_comorb['risco_relativo']:.2f})")
        
        print("\n💡 RECOMENDAÇÕES CLÍNICAS")
        
        if dados['prevalencia_hipertensao'] > 40:
            print("  🔴 Alta prevalência de hipertensão - implementar screening sistemático")
        
        if sindrome['prevalencia_sindrome'] > 25:
            print("  🔴 Alta prevalência de síndrome metabólica - focar em mudanças de estilo de vida")
        
        if comorbidades.get('obesidade', {}).get('prevalencia_geral', 0) > 30:
            print("  ⚠️ Alta prevalência de obesidade - programas de controle de peso")
        
        if comorbidades.get('diabetes', {}).get('prevalencia_geral', 0) > 10:
            print("  💊 Monitoramento glicêmico rigoroso necessário")
        
        print("  📋 Implementar estratificação de risco cardiovascular")
        print("  🎯 Abordagem multidisciplinar recomendada")


def create_medical_analyzer() -> MedicalAnalyzer:
    """
    Função de conveniência para criar analisador médico.
    
    Returns:
        Instância do MedicalAnalyzer
    """
    return MedicalAnalyzer()


if __name__ == "__main__":
    print("🧪 Testando módulo MedicalAnalyzer...")
    
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
        'glicose': np.random.normal(95, 20, n_samples),
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'fumante_atualmente': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'medicamento_pressao': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'risco_hipertensao': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    # Testar analisador
    analyzer = MedicalAnalyzer()
    report = analyzer.create_medical_report(test_data)
    
    print("\n✅ Teste concluído!")
    print("🏥 MedicalAnalyzer pronto para uso")