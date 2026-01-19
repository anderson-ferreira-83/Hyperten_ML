"""
Setup Universal para todos os notebooks do projeto TCC Hipertensão ML
Execute este código no início de qualquer notebook para garantir que todas as funções básicas funcionem
"""

# ========================================
# IMPORTAÇÕES BÁSICAS (SEMPRE FUNCIONAM)
# ========================================
import sys
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Garantir que estamos no diretório correto
current_dir = Path.cwd()
if current_dir.name == 'notebooks':
    project_root = current_dir.parent
else:
    project_root = current_dir

# Adicionar src ao path Python
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print(f"📁 Diretório do projeto: {project_root}")
print(f"📁 Diretório src adicionado: {src_path}")

# ========================================
# IMPORTAÇÕES CIENTÍFICAS ESSENCIAIS
# ========================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
import json

# ========================================
# IMPORTAÇÕES OPCIONAIS COM FALLBACK
# ========================================
# Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
    print("✅ Plotly disponível")
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️ Plotly não disponível - usando matplotlib/seaborn")

# Scikit-learn
try:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
    print("✅ Scikit-learn disponível")
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn não disponível - funcionalidades básicas apenas")

# Imbalanced-learn (SMOTE)
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
    print("✅ Imbalanced-learn (SMOTE) disponível")
except ImportError:
    SMOTE_AVAILABLE = False
    print("⚠️ SMOTE não disponível")

# ========================================
# FUNÇÕES UNIVERSAIS (SEMPRE FUNCIONAM)
# ========================================

def print_section(title, char="=", width=80):
    """Imprime uma seção formatada"""
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}")

def save_figure(fig, name, subfolder='eda'):
    """Salva figura com tratamento robusto de erros"""
    try:
        results_dir = project_root / '04_reports'
        results_dir.mkdir(exist_ok=True)
        
        if subfolder:
            subfolder_dir = results_dir / subfolder
            subfolder_dir.mkdir(exist_ok=True)
            filepath = subfolder_dir / f'{name}.png'
        else:
            filepath = results_dir / f'{name}.png'
            
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"💾 Figura salva: {filepath}")
        return filepath
    except Exception as e:
        print(f"⚠️ Erro ao salvar figura {name}: {e}")
        return None

def setup_plotting_style():
    """Configura estilo padrão dos plots"""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9

def get_results_path(subfolder=''):
    """Retorna caminho para diretório de resultados"""
    results_path = project_root / '04_reports'
    if subfolder:
        results_path = results_path / subfolder
    results_path.mkdir(parents=True, exist_ok=True)
    return results_path

def load_config():
    """Carrega configuração básica"""
    return {
        'data': {
            'target_column': 'risco_hipertensao',
            'test_size': 0.2,
            'random_state': 42
        },
        'paths': {
            'data_dir': str(project_root / '00_data'),
            'results_dir': str(project_root / '04_reports'),
            'figures_dir': str(project_root / '04_reports' / 'figures')
        },
        'model': {
            'random_state': 42,
            'cv_folds': 5
        }
    }

# ========================================
# CARREGAMENTO DE DADOS ROBUSTO
# ========================================

def load_hypertension_data():
    """
    Carrega dados de hipertensão com múltiplas tentativas e fallbacks
    """
    print_section("CARREGAMENTO DE DADOS DE HIPERTENSÃO")
    
    # Possíveis caminhos para o arquivo (priorizando caminhos corretos)
    possible_paths = [
        project_root / "00_data" / "raw" / "Hypertension-risk-model-main.csv",
        "00_data/raw/Hypertension-risk-model-main.csv",
        "hypertension_data.csv"
    ]
    
    # Tentar carregar de diferentes locais
    for path in possible_paths:
        try:
            if Path(path).exists():
                print(f"✅ Arquivo encontrado: {path}")
                df = pd.read_csv(path)
                
                # Traduzir colunas se necessário
                df = translate_columns(df)
                print(f"📊 Dados carregados: {df.shape}")
                print(f"📋 Colunas: {list(df.columns)}")
                return df
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar {path}: {e}")
            continue
    
    print("❌ Arquivo não encontrado. Criando dados simulados...")
    return create_simulated_data()

def translate_columns(df):
    """Traduz nomes das colunas para português"""
    
    column_translation = {
        'sex': 'sexo',
        'male': 'sexo', 
        'age': 'idade',
        'currentSmoker': 'fumante_atualmente',
        'cigsPerDay': 'cigarros_por_dia',
        'BPMeds': 'medicamento_pressao',
        'diabetes': 'diabetes',
        'totChol': 'colesterol_total',
        'sysBP': 'pressao_sistolica',
        'diaBP': 'pressao_diastolica',
        'BMI': 'imc',
        'heartRate': 'frequencia_cardiaca',
        'glucose': 'glicose',
        'TenYearCHD': 'risco_hipertensao',
        'Risk': 'risco_hipertensao'
    }
    
    # Aplicar tradução apenas para colunas existentes
    new_columns = {}
    for col in df.columns:
        if col in column_translation:
            new_columns[col] = column_translation[col]
        else:
            new_columns[col] = col
    
    df = df.rename(columns=new_columns)
    print(f"🔤 Colunas traduzidas para português")
    return df

def create_simulated_data(n_samples=4240):
    """Cria dados simulados realistas para demonstração"""
    print("🔄 Criando dados simulados realistas...")
    
    np.random.seed(42)
    
    # Gerar dados correlacionados
    ages = np.random.randint(32, 71, n_samples)
    
    # Pressão sistólica correlacionada com idade
    systolic_base = 100 + ages * 0.8 + np.random.normal(0, 15, n_samples)
    systolic_bp = np.clip(systolic_base, 85, 200)
    
    # Pressão diastólica correlacionada com sistólica
    diastolic_bp = 0.6 * systolic_bp + np.random.normal(20, 8, n_samples)
    diastolic_bp = np.clip(diastolic_bp, 50, 130)
    
    # IMC com variação por idade
    bmi_base = 22 + (ages - 40) * 0.1 + np.random.normal(0, 4, n_samples)
    bmi = np.clip(bmi_base, 16, 45)
    
    # Risco baseado em múltiplos fatores
    risk_prob = (0.1 + (ages - 30) * 0.015 + 
                (systolic_bp - 120) * 0.008 + 
                (bmi - 25) * 0.02)
    risk_prob = np.clip(risk_prob, 0.05, 0.85)
    
    df = pd.DataFrame({
        'sexo': np.random.choice([0, 1], n_samples, p=[0.57, 0.43]),
        'idade': ages,
        'fumante_atualmente': np.random.choice([0, 1], n_samples, p=[0.51, 0.49]),
        'cigarros_por_dia': np.where(
            np.random.choice([0, 1], n_samples, p=[0.51, 0.49]),
            np.random.exponential(8, n_samples), 0
        ),
        'medicamento_pressao': np.random.choice([0, 1], n_samples, p=[0.97, 0.03]),
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.97, 0.03]),
        'colesterol_total': np.random.normal(237, 45, n_samples),
        'pressao_sistolica': systolic_bp,
        'pressao_diastolica': diastolic_bp,
        'imc': bmi,
        'frequencia_cardiaca': np.random.normal(76, 12, n_samples),
        'glicose': np.random.normal(82, 24, n_samples),
        'risco_hipertensao': np.random.binomial(1, risk_prob, n_samples)
    })
    
    # Adicionar alguns valores ausentes realistas
    missing_indices = {
        'colesterol_total': np.random.choice(df.index, 50, replace=False),
        'cigarros_por_dia': np.random.choice(df.index, 30, replace=False),
        'glicose': np.random.choice(df.index, 400, replace=False),
        'medicamento_pressao': np.random.choice(df.index, 53, replace=False),
        'imc': np.random.choice(df.index, 19, replace=False)
    }
    
    for col, indices in missing_indices.items():
        df.loc[indices, col] = np.nan
    
    print(f"📊 Dados simulados criados: {df.shape}")
    print(f"⚠️ Valores ausentes adicionados: {df.isnull().sum().sum()}")
    return df

# ========================================
# PRÉ-PROCESSAMENTO BÁSICO
# ========================================

def basic_preprocessing(df, target_col='risco_hipertensao'):
    """Aplica pré-processamento básico aos dados"""
    print_section("PRÉ-PROCESSAMENTO BÁSICO")
    
    df_processed = df.copy()
    
    # 1. Identificar colunas numéricas e categóricas
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    
    print(f"📊 Colunas numéricas: {len(numeric_cols)}")
    
    # 2. Tratamento de valores ausentes
    missing_count_before = df_processed.isnull().sum().sum()
    if missing_count_before > 0:
        print(f"🔧 Tratando {missing_count_before} valores ausentes...")
        
        for col in numeric_cols:
            if df_processed[col].isnull().sum() > 0:
                median_value = df_processed[col].median()
                df_processed[col].fillna(median_value, inplace=True)
        
        missing_count_after = df_processed.isnull().sum().sum()
        print(f"✅ Valores ausentes restantes: {missing_count_after}")
    
    # 3. Verificar dados do target
    if target_col in df_processed.columns:
        target_dist = df_processed[target_col].value_counts()
        print(f"🎯 Distribuição do target '{target_col}':")
        for val, count in target_dist.items():
            pct = (count / len(df_processed)) * 100
            print(f"   {val}: {count} ({pct:.1f}%)")
    
    return df_processed

# ========================================
# FEATURE ENGINEERING BÁSICO
# ========================================

def create_basic_features(df):
    """Cria features básicas derivadas"""
    print("🔧 Criando features básicas...")
    
    df_enhanced = df.copy()
    created_features = []
    
    # Features de pressão arterial
    if 'pressao_sistolica' in df.columns and 'pressao_diastolica' in df.columns:
        df_enhanced['pressao_arterial_media'] = (2 * df_enhanced['pressao_diastolica'] + df_enhanced['pressao_sistolica']) / 3
        df_enhanced['pressao_pulso'] = df_enhanced['pressao_sistolica'] - df_enhanced['pressao_diastolica']
        created_features.extend(['pressao_arterial_media', 'pressao_pulso'])
    
    # Features de idade
    if 'idade' in df.columns:
        df_enhanced['decada_idade'] = (df_enhanced['idade'] // 10).astype(int)
        created_features.append('decada_idade')
    
    # Features de IMC
    if 'imc' in df.columns:
        df_enhanced['categoria_imc'] = pd.cut(df_enhanced['imc'], 
                                            bins=[0, 18.5, 25, 30, 50], 
                                            labels=[0, 1, 2, 3]).astype(float)
        created_features.append('categoria_imc')
    
    print(f"✅ {len(created_features)} features criadas: {created_features}")
    return df_enhanced, created_features

# ========================================
# CONFIGURAÇÃO INICIAL
# ========================================

# Configurar estilo de plotagem
setup_plotting_style()

# Status do setup
print_section("STATUS DO SETUP UNIVERSAL")
print(f"✅ Python: {sys.version.split()[0]}")
print(f"✅ Pandas: {pd.__version__}")
print(f"✅ NumPy: {np.__version__}")
print(f"✅ Matplotlib: {plt.matplotlib.__version__}")
print(f"✅ Seaborn: {sns.__version__}")
print(f"🎨 Plotly: {'✅ ' + px.__version__ if PLOTLY_AVAILABLE else '❌ Não disponível'}")
print(f"🤖 Scikit-learn: {'✅ Disponível' if SKLEARN_AVAILABLE else '❌ Não disponível'}")
print(f"⚖️ SMOTE: {'✅ Disponível' if SMOTE_AVAILABLE else '❌ Não disponível'}")
print(f"📁 Diretório do projeto: {project_root}")

print("\n🎉 Setup universal concluído! Todas as funções básicas estão disponíveis.")
print("📝 Para usar em um notebook:")
print("   1. Execute: exec(open('02_notebooks/SETUP_UNIVERSAL.py').read())")
print("   2. Use: df = load_hypertension_data()")
print("   3. Continue com suas análises!")