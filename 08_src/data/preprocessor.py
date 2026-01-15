"""
Módulo para pré-processamento de dados.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import logging

from ..utils.config import load_config
from ..utils.helpers import print_section, cap_outliers_iqr, create_missing_values_report


class DataPreprocessor:
    """
    Classe para pré-processamento completo dos dados.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o preprocessador.
        
        Args:
            config: Configuração opcional
        """
        self.config = config if config else load_config()
        self.preprocessing_config = self.config.get('preprocessing', {})
        self.scaler = None
        self.feature_columns = None
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trata valores ausentes baseado na configuração.
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame com valores ausentes tratados
        """
        print_section("TRATAMENTO DE VALORES AUSENTES")
        
        df_copy = df.copy()
        missing_config = self.preprocessing_config.get('missing_values', {})
        strategy = missing_config.get('strategy', 'median')
        
        # Relatório inicial
        missing_report = create_missing_values_report(df_copy)
        if len(missing_report) > 0:
            print("📊 Valores ausentes encontrados:")
            print(missing_report.to_string(index=False))
        else:
            print("✅ Nenhum valor ausente encontrado")
            return df_copy
        
        # Identificar colunas numéricas e categóricas
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_copy.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Tratar colunas numéricas
        for col in numeric_cols:
            if df_copy[col].isnull().sum() > 0:
                if strategy == 'mean':
                    fill_value = df_copy[col].mean()
                elif strategy == 'median':
                    fill_value = df_copy[col].median()
                elif strategy == 'mode':
                    fill_value = df_copy[col].mode()[0] if len(df_copy[col].mode()) > 0 else df_copy[col].median()
                else:
                    fill_value = 0
                
                missing_count = df_copy[col].isnull().sum()
                df_copy[col].fillna(fill_value, inplace=True)
                print(f"  ✓ {col}: {missing_count} valores preenchidos com {strategy} = {fill_value:.2f}")
        
        # Tratar colunas categóricas
        categorical_strategy = missing_config.get('categorical_strategy', 'mode')
        for col in categorical_cols:
            if df_copy[col].isnull().sum() > 0:
                if categorical_strategy == 'mode':
                    fill_value = df_copy[col].mode()[0] if len(df_copy[col].mode()) > 0 else 'Unknown'
                else:
                    fill_value = 'Unknown'
                
                missing_count = df_copy[col].isnull().sum()
                df_copy[col].fillna(fill_value, inplace=True)
                print(f"  ✓ {col}: {missing_count} valores preenchidos com '{fill_value}'")
        
        # Verificação final
        remaining_missing = df_copy.isnull().sum().sum()
        print(f"\n📈 Resultado: {remaining_missing} valores ausentes restantes")
        
        return df_copy
    
    def handle_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Trata outliers usando método especificado na configuração.
        
        Args:
            df: DataFrame com dados
            columns: Lista de colunas para tratar (None = todas numéricas)
            
        Returns:
            DataFrame com outliers tratados
        """
        print_section("TRATAMENTO DE OUTLIERS")
        
        outliers_config = self.preprocessing_config.get('outliers', {})
        method = outliers_config.get('method', 'iqr')
        threshold = outliers_config.get('threshold', 1.5)
        
        if columns is None:
            # Usar todas as colunas numéricas exceto target
            target_col = self.config.get('data', {}).get('target_column', 'risco_hipertensao')
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if target_col in columns:
                columns.remove(target_col)
        
        print(f"🎯 Método: {method.upper()}")
        print(f"📏 Threshold: {threshold}")
        print(f"📊 Colunas a processar: {columns}")
        
        df_copy = df.copy()
        
        if method == 'iqr':
            df_copy = cap_outliers_iqr(df_copy, columns, factor=threshold)
        elif method == 'zscore':
            # Implementar z-score se necessário
            print("⚠️  Método z-score não implementado ainda, usando IQR")
            df_copy = cap_outliers_iqr(df_copy, columns, factor=threshold)
        else:
            print(f"⚠️  Método '{method}' não reconhecido, usando IQR")
            df_copy = cap_outliers_iqr(df_copy, columns, factor=threshold)
        
        return df_copy
    
    def scale_features(self, X_train: pd.DataFrame, X_test: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Aplica escalonamento nas features.
        
        Args:
            X_train: Features de treino
            X_test: Features de teste (opcional)
            
        Returns:
            Tuple com features escalonadas
        """
        print_section("ESCALONAMENTO DE FEATURES")
        
        scaling_config = self.preprocessing_config.get('scaling', {})
        method = scaling_config.get('method', 'standard')
        
        # Selecionar scaler
        if method == 'standard':
            self.scaler = StandardScaler()
            print("📏 Usando StandardScaler (z-score)")
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
            print("📏 Usando MinMaxScaler (0-1)")
        elif method == 'robust':
            self.scaler = RobustScaler()
            print("📏 Usando RobustScaler (mediana e IQR)")
        else:
            print(f"⚠️  Método '{method}' não reconhecido, usando StandardScaler")
            self.scaler = StandardScaler()
        
        # Aplicar escalonamento
        self.feature_columns = X_train.columns.tolist()
        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        
        print(f"✓ Features de treino escalonadas: {X_train_scaled.shape}")
        
        X_test_scaled = None
        if X_test is not None:
            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )
            print(f"✓ Features de teste escalonadas: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled
    
    def split_data(self, df: pd.DataFrame, test_size: float = 0.25, stratify: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Divide dados em treino e teste.
        
        Args:
            df: DataFrame completo
            test_size: Proporção para teste
            stratify: Se deve estratificar pela variável target
            
        Returns:
            Tuple com (X_train, X_test, y_train, y_test)
        """
        print_section(f"DIVISÃO DOS DADOS ({int((1-test_size)*100)}/{int(test_size*100)})")
        
        # Obter configurações
        target_col = self.config.get('data', {}).get('target_column', 'risco_hipertensao')
        random_state = self.config.get('general', {}).get('random_state', 42)
        
        # Separar features e target
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        print(f"🎯 Variável target: {target_col}")
        print(f"📊 Total de amostras: {len(df)}")
        print(f"📈 Features: {len(X.columns)}")
        
        # Dividir dados
        stratify_param = y if stratify else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_param
        )
        
        print(f"🏋️  Treino: {len(X_train)} amostras ({len(X_train)/len(df)*100:.1f}%)")
        print(f"🧪 Teste: {len(X_test)} amostras ({len(X_test)/len(df)*100:.1f}%)")
        
        # Verificar distribuição das classes
        if stratify:
            print("\n📊 Distribuição de classes:")
            train_dist = y_train.value_counts(normalize=True).sort_index()
            test_dist = y_test.value_counts(normalize=True).sort_index()
            
            for class_val in sorted(y.unique()):
                train_pct = train_dist.get(class_val, 0) * 100
                test_pct = test_dist.get(class_val, 0) * 100
                print(f"  Classe {class_val}: Treino {train_pct:.1f}% | Teste {test_pct:.1f}%")
        
        return X_train, X_test, y_train, y_test
    
    def apply_smote(self, X_train: pd.DataFrame, y_train: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Aplica SMOTE para balanceamento de classes.
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            
        Returns:
            Tuple com dados balanceados
        """
        print_section("APLICAÇÃO DO SMOTE")
        
        # Configuração do SMOTE
        smote_config = self.config.get('smote', {})
        sampling_strategy = smote_config.get('sampling_strategy', 'auto')
        k_neighbors = smote_config.get('k_neighbors', 5)
        random_state = smote_config.get('random_state', 42)
        
        # Distribuição antes do SMOTE
        print("📊 Distribuição ANTES do SMOTE:")
        original_dist = y_train.value_counts().sort_index()
        total_original = len(y_train)
        
        for class_val, count in original_dist.items():
            percentage = count / total_original * 100
            print(f"  Classe {class_val}: {count} amostras ({percentage:.1f}%)")
        
        imbalance_ratio = original_dist.max() / original_dist.min()
        print(f"📏 Razão de desbalanceamento: 1:{imbalance_ratio:.2f}")
        
        # Aplicar SMOTE
        smote = SMOTE(
            sampling_strategy=sampling_strategy,
            k_neighbors=k_neighbors,
            random_state=random_state
        )
        
        print(f"\n⚙️  Configurações do SMOTE:")
        print(f"  📊 Estratégia: {sampling_strategy}")
        print(f"  👥 K-neighbors: {k_neighbors}")
        print(f"  🎲 Random state: {random_state}")
        
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        # Converter de volta para DataFrame/Series
        X_train_balanced = pd.DataFrame(
            X_train_balanced,
            columns=X_train.columns
        )
        y_train_balanced = pd.Series(y_train_balanced, name=y_train.name)
        
        # Distribuição depois do SMOTE
        print("\n📊 Distribuição DEPOIS do SMOTE:")
        balanced_dist = y_train_balanced.value_counts().sort_index()
        total_balanced = len(y_train_balanced)
        
        for class_val, count in balanced_dist.items():
            percentage = count / total_balanced * 100
            print(f"  Classe {class_val}: {count} amostras ({percentage:.1f}%)")
        
        # Estatísticas
        synthetic_samples = total_balanced - total_original
        print(f"\n📈 Estatísticas:")
        print(f"  🔢 Amostras originais: {total_original}")
        print(f"  🔢 Amostras após SMOTE: {total_balanced}")
        print(f"  🆕 Amostras sintéticas criadas: {synthetic_samples}")
        print(f"  📊 Percentual sintético: {synthetic_samples/total_balanced*100:.1f}%")
        
        return X_train_balanced, y_train_balanced
    
    def full_preprocessing_pipeline(self, df: pd.DataFrame, apply_smote_flag: bool = True) -> Dict[str, Union[pd.DataFrame, pd.Series]]:
        """
        Executa pipeline completo de pré-processamento.
        
        Args:
            df: DataFrame original
            apply_smote_flag: Se deve aplicar SMOTE
            
        Returns:
            Dict com todos os dados processados
        """
        print_section("PIPELINE COMPLETO DE PRÉ-PROCESSAMENTO", "=", 100)
        
        # 1. Tratar valores ausentes
        df_no_missing = self.handle_missing_values(df)
        
        # 2. Tratar outliers
        df_no_outliers = self.handle_outliers(df_no_missing)
        
        # 3. Dividir dados
        test_size = self.config.get('general', {}).get('test_size', 0.25)
        X_train, X_test, y_train, y_test = self.split_data(df_no_outliers, test_size=test_size)
        
        # 4. Escalonar features
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        # 5. Aplicar SMOTE (opcional)
        if apply_smote_flag:
            X_train_balanced, y_train_balanced = self.apply_smote(X_train_scaled, y_train)
        else:
            X_train_balanced, y_train_balanced = X_train_scaled, y_train
        
        print_section("✅ PIPELINE CONCLUÍDO COM SUCESSO", "=", 100)
        
        result = {
            'X_train': X_train_balanced,
            'X_test': X_test_scaled,
            'y_train': y_train_balanced,
            'y_test': y_test,
            'X_train_original': X_train,
            'X_train_scaled': X_train_scaled,
            'processed_data': df_no_outliers
        }
        
        return result


def create_preprocessor(config: Optional[Dict] = None) -> DataPreprocessor:
    """
    Função de conveniência para criar preprocessador.
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do DataPreprocessor
    """
    return DataPreprocessor(config)


if __name__ == "__main__":
    # Teste do módulo
    print("🧪 Testando módulo DataPreprocessor...")
    
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    test_data = pd.DataFrame({
        'idade': np.random.randint(30, 80, n_samples),
        'pressao_sistolica': np.random.normal(130, 20, n_samples),
        'pressao_diastolica': np.random.normal(85, 15, n_samples),
        'imc': np.random.normal(25, 5, n_samples),
        'risco_hipertensao': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    # Adicionar alguns valores ausentes
    test_data.loc[:10, 'pressao_sistolica'] = np.nan
    test_data.loc[:5, 'imc'] = np.nan
    
    # Testar preprocessador
    preprocessor = DataPreprocessor()
    results = preprocessor.full_preprocessing_pipeline(test_data)
    
    print(f"\n✅ Teste concluído!")
    print(f"📊 Shape final - Treino: {results['X_train'].shape}, Teste: {results['X_test'].shape}")