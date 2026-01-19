"""
Módulo para carregamento e gestão de dados.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

from ..utils.config import get_data_path, load_config
from ..utils.helpers import print_section, memory_usage_report


class DataLoader:
    """
    Classe responsável pelo carregamento e gerenciamento inicial dos dados.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o DataLoader.
        
        Args:
            config: Dicionário de configuração opcional
        """
        self.config = config if config else load_config()
        self.data_config = self.config.get('data', {})
        self.raw_data = None
        self.processed_data = None
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_raw_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega dados brutos do CSV.
        
        Args:
            file_path: Caminho para arquivo CSV (opcional)
            
        Returns:
            DataFrame com dados brutos
        """
        if file_path is None:
            # Usar configuração padrão
            file_name = self.data_config.get('file_name', 'Hypertension-risk-model-main.csv')
            file_path = get_data_path('raw') / file_name
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {file_path}")
        
        print_section(f"CARREGANDO DADOS: {file_path.name}")
        
        # Carregar dados
        try:
            self.raw_data = pd.read_csv(file_path)
            self.logger.info(f"Dados carregados com sucesso: {self.raw_data.shape}")
            
            # Relatório básico
            self._print_data_info()
            
            return self.raw_data
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def translate_columns(self) -> pd.DataFrame:
        """
        Traduz nomes das colunas usando mapeamento da configuração.
        
        Returns:
            DataFrame com colunas traduzidas
        """
        if self.raw_data is None:
            raise ValueError("Dados não carregados. Execute load_raw_data() primeiro.")
        
        column_mapping = self.data_config.get('column_mapping', {})
        
        if column_mapping:
            print_section("TRADUZINDO COLUNAS")
            self.processed_data = self.raw_data.rename(columns=column_mapping)
            
            # Mostrar mapeamento
            for original, translated in column_mapping.items():
                if original in self.raw_data.columns:
                    print(f"  {original} -> {translated}")
            
            self.logger.info("Colunas traduzidas com sucesso")
        else:
            self.processed_data = self.raw_data.copy()
            self.logger.info("Nenhum mapeamento de colunas encontrado")
        
        return self.processed_data
    
    def get_column_info(self) -> pd.DataFrame:
        """
        Retorna informações detalhadas sobre as colunas.
        
        Returns:
            DataFrame com informações das colunas
        """
        if self.processed_data is None:
            data = self.raw_data
        else:
            data = self.processed_data
            
        if data is None:
            raise ValueError("Nenhum dado carregado")
        
        column_info = pd.DataFrame({
            'Column': data.columns,
            'Data_Type': data.dtypes,
            'Non_Null_Count': data.count(),
            'Null_Count': data.isnull().sum(),
            'Null_Percentage': (data.isnull().sum() / len(data)) * 100,
            'Unique_Values': [data[col].nunique() for col in data.columns],
            'Memory_Usage_KB': data.memory_usage(deep=True)[1:] / 1024
        })
        
        return column_info
    
    def get_target_distribution(self) -> Dict[str, float]:
        """
        Analisa distribuição da variável target.
        
        Returns:
            Dict com informações da distribuição
        """
        target_col = self.data_config.get('target_column', 'risco_hipertensao')
        
        if self.processed_data is None:
            data = self.raw_data
        else:
            data = self.processed_data
            
        if data is None or target_col not in data.columns:
            raise ValueError(f"Coluna target '{target_col}' não encontrada")
        
        value_counts = data[target_col].value_counts()
        total = len(data)
        
        distribution = {
            'total_samples': total,
            'class_counts': value_counts.to_dict(),
            'class_percentages': (value_counts / total * 100).to_dict(),
            'imbalance_ratio': value_counts.max() / value_counts.min()
        }
        
        return distribution
    
    def save_processed_data(self, file_name: str = "processed_data.csv"):
        """
        Salva dados processados.
        
        Args:
            file_name: Nome do arquivo para salvar
        """
        if self.processed_data is None:
            raise ValueError("Nenhum dado processado para salvar")
        
        save_path = get_data_path('processed') / file_name
        self.processed_data.to_csv(save_path, index=False)
        
        self.logger.info(f"Dados processados salvos em: {save_path}")
    
    def _print_data_info(self):
        """
        Imprime informações básicas sobre os dados carregados.
        """
        if self.raw_data is None:
            return
        
        print(f"📊 Formato dos dados: {self.raw_data.shape}")
        print(f"📋 Colunas: {list(self.raw_data.columns)}")
        print(f"💾 Uso de memória: {self.raw_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Tipos de dados
        print("\n📈 Tipos de dados:")
        for dtype, count in self.raw_data.dtypes.value_counts().items():
            print(f"  {dtype}: {count} colunas")
        
        # Valores ausentes
        missing_total = self.raw_data.isnull().sum().sum()
        if missing_total > 0:
            print(f"\n⚠️  Total de valores ausentes: {missing_total}")
        else:
            print("\n✅ Nenhum valor ausente encontrado")


# Função de conveniência para uso rápido
def load_hypertension_data(translate_columns: bool = True) -> Tuple[pd.DataFrame, DataLoader]:
    """
    Função de conveniência para carregar dados de hipertensão.
    
    Args:
        translate_columns: Se deve traduzir os nomes das colunas
        
    Returns:
        Tuple com (DataFrame, DataLoader instance)
    """
    loader = DataLoader()
    data = loader.load_raw_data()
    
    if translate_columns:
        data = loader.translate_columns()
    
    return data, loader


if __name__ == "__main__":
    # Teste do módulo
    loader = DataLoader()
    
    try:
        data = loader.load_raw_data()
        data_translated = loader.translate_columns()
        
        print("\n" + "="*50)
        print("INFORMAÇÕES DAS COLUNAS")
        print("="*50)
        print(loader.get_column_info())
        
        print("\n" + "="*50)
        print("DISTRIBUIÇÃO DO TARGET")
        print("="*50)
        target_dist = loader.get_target_distribution()
        for key, value in target_dist.items():
            print(f"{key}: {value}")
        
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
        print("Coloque o arquivo de dados em 00_data/raw/ para testar o módulo")