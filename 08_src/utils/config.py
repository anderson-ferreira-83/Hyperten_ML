"""
Módulo de configuração para carregar parâmetros do projeto.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_file: str = "experiment_config.yaml") -> Dict[str, Any]:
    """
    Carrega arquivo de configuração YAML.
    
    Args:
        config_file: Nome do arquivo de configuração
        
    Returns:
        Dict com configurações carregadas
    """
    # Encontrar o diretório raiz do projeto
    current_dir = Path(__file__).parent.parent.parent
    config_path = current_dir / "09_config" / config_file
    
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config


def load_model_params(config_file: str = "model_params.yaml") -> Dict[str, Any]:
    """
    Carrega parâmetros específicos dos modelos.
    
    Args:
        config_file: Nome do arquivo de parâmetros dos modelos
        
    Returns:
        Dict com parâmetros dos modelos
    """
    return load_config(config_file)


def get_project_root() -> Path:
    """
    Retorna o diretório raiz do projeto.
    
    Returns:
        Path do diretório raiz
    """
    return Path(__file__).parent.parent.parent


def get_data_path(subfolder: str = "raw") -> Path:
    """
    Retorna caminho para diretório de dados.
    
    Args:
        subfolder: Subpasta (raw, processed, external)
        
    Returns:
        Path para diretório de dados
    """
    return get_project_root() / "00_data" / subfolder


def get_results_path(subfolder: str = "figures") -> Path:
    """
    Retorna caminho para diretório de resultados.
    
    Args:
        subfolder: Subpasta (figures, models, reports)
        
    Returns:
        Path para diretório de resultados
    """
    results_path = get_project_root() / "04_reports" / subfolder
    results_path.mkdir(parents=True, exist_ok=True)
    return results_path


def ensure_directories():
    """
    Garante que todos os diretórios necessários existam.
    """
    root = get_project_root()
    
    directories = [
        "00_data/raw",
        "00_data/processed", 
        "data/external",
        "04_reports/figures/eda",
        "04_reports/figures/models",
        "04_reports/figures/comparisons",
        "04_reports/modeling",
        "04_reports/reports"
    ]
    
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Teste das funções
    ensure_directories()
    config = load_config()
    print("Configuração carregada com sucesso!")
    print(f"Projeto localizado em: {get_project_root()}")
