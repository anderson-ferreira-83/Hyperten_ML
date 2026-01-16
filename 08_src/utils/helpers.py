"""
Funções auxiliares e utilitários gerais.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path


def setup_plotting_style():
    """
    Configura estilo padrão para gráficos.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette('husl')
    
    # Configurações globais
    plt.rcParams.update({
        'figure.figsize': (10, 6),
        'figure.dpi': 300,
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'legend.title_fontsize': 11
    })


def save_figure(
    fig,
    name: str,
    subfolder: str = "eda",
    formats: Optional[List[str]] = None,
    dpi: int = 400,
    save_axes: bool = False,
    legend_outside: bool = True,
    axes_suffix: str = "ax",
):
    """
    Salva figura em diretorio apropriado com qualidade de publicacao.

    Args:
        fig: Objeto matplotlib figure
        name: Nome do arquivo (sem extensao)
        subfolder: Subpasta em 04_reports/figures/
        formats: Lista de formatos (png, pdf, svg)
        dpi: DPI para resolucao
        save_axes: Salvar subplots individualmente quando houver mais de um eixo
        legend_outside: Move legendas para fora do eixo
        axes_suffix: Sufixo usado nos arquivos dos subplots
    """
    from .config import get_results_path

    save_path = get_results_path("figures") / subfolder
    save_path.mkdir(parents=True, exist_ok=True)

    if formats is None:
        formats = ["png", "pdf", "svg"]

    if legend_outside:
        for ax in fig.axes:
            legend = ax.get_legend()
            if legend:
                legend.set_loc("upper left")
                legend.set_bbox_to_anchor((1.02, 1.0))
                if hasattr(legend, "set_frameon"):
                    legend.set_frameon(True)
                elif legend.get_frame():
                    legend.get_frame().set_visible(True)

    save_kwargs = {
        "dpi": dpi,
        "bbox_inches": "tight",
        "facecolor": "white",
        "pad_inches": 0.2,
    }

    for fmt in formats:
        file_path = save_path / f"{name}.{fmt}"
        fig.savefig(file_path, format=fmt, **save_kwargs)

    if save_axes and len(fig.axes) > 1:
        try:
            from matplotlib.transforms import Bbox

            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            ax_save_kwargs = save_kwargs.copy()
            ax_save_kwargs.pop("bbox_inches", None)

            for idx, ax in enumerate(fig.axes, 1):
                if not ax.get_visible():
                    continue
                bbox = ax.get_tightbbox(renderer)
                legend = ax.get_legend()
                if legend:
                    bbox = Bbox.union([bbox, legend.get_tightbbox(renderer)])
                bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

                for fmt in formats:
                    ax_file = save_path / f"{name}_{axes_suffix}{idx:02d}.{fmt}"
                    fig.savefig(ax_file, format=fmt, bbox_inches=bbox, **ax_save_kwargs)
        except Exception as e:
            print(f"Aviso: Falha ao salvar subplots individuais: {e}")

    print(f"Figura salva em: {save_path / name}")


def print_section(title: str, char: str = "=", width: int = 80):
    """
    Imprime seção formatada para organizar output.
    
    Args:
        title: Título da seção
        char: Caractere para a linha
        width: Largura da linha
    """
    line = char * width
    print(f"\n{line}")
    print(f" {title.upper()}")
    print(line)


def calculate_basic_stats(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calcula estatísticas básicas para uma coluna.
    
    Args:
        df: DataFrame
        column: Nome da coluna
        
    Returns:
        Dict com estatísticas
    """
    return {
        'count': df[column].count(),
        'missing': df[column].isnull().sum(),
        'missing_pct': df[column].isnull().sum() / len(df) * 100,
        'mean': df[column].mean(),
        'median': df[column].median(),
        'std': df[column].std(),
        'min': df[column].min(),
        'max': df[column].max(),
        'q25': df[column].quantile(0.25),
        'q75': df[column].quantile(0.75)
    }


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Series:
    """
    Detecta outliers usando método IQR.
    
    Args:
        df: DataFrame
        column: Nome da coluna
        factor: Fator multiplicativo para IQR
        
    Returns:
        Series boolean indicando outliers
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    
    return (df[column] < lower_bound) | (df[column] > upper_bound)


def cap_outliers_iqr(df: pd.DataFrame, columns: List[str], factor: float = 1.5) -> pd.DataFrame:
    """
    Aplica capping de outliers usando método IQR.
    
    Args:
        df: DataFrame
        columns: Lista de colunas para aplicar capping
        factor: Fator multiplicativo para IQR
        
    Returns:
        DataFrame com outliers tratados
    """
    df_copy = df.copy()
    
    for column in columns:
        Q1 = df_copy[column].quantile(0.25)
        Q3 = df_copy[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        df_copy[column] = np.clip(df_copy[column], lower_bound, upper_bound)
        
        outliers_count = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
        print(f"Coluna {column}: {outliers_count} outliers tratados")
    
    return df_copy


def create_missing_values_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria relatório detalhado de valores ausentes.
    
    Args:
        df: DataFrame
        
    Returns:
        DataFrame com relatório de missing values
    """
    missing_data = pd.DataFrame({
        'Column': df.columns,
        'Missing_Count': df.isnull().sum(),
        'Missing_Percentage': (df.isnull().sum() / len(df)) * 100,
        'Data_Type': df.dtypes
    })
    
    missing_data = missing_data[missing_data['Missing_Count'] > 0]
    missing_data = missing_data.sort_values('Missing_Percentage', ascending=False)
    
    return missing_data.reset_index(drop=True)


def memory_usage_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera relatório de uso de memória do DataFrame.
    
    Args:
        df: DataFrame
        
    Returns:
        Dict com informações de memória
    """
    memory_info = {
        'total_memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'shape': df.shape,
        'columns': len(df.columns),
        'memory_per_column': df.memory_usage(deep=True) / 1024**2
    }
    
    return memory_info


def format_number(num: float, decimals: int = 2) -> str:
    """
    Formata número para exibição.
    
    Args:
        num: Número para formatar
        decimals: Número de casas decimais
        
    Returns:
        String formatada
    """
    if pd.isna(num):
        return "N/A"
    
    if abs(num) >= 1000000:
        return f"{num/1000000:.{decimals}f}M"
    elif abs(num) >= 1000:
        return f"{num/1000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def create_correlation_summary(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """
    Cria resumo de correlações com variável target.
    
    Args:
        df: DataFrame
        target_col: Nome da coluna target
        
    Returns:
        DataFrame com correlações ordenadas
    """
    correlations = df.corr(numeric_only=True)[target_col].drop(target_col)
    
    corr_summary = pd.DataFrame({
        'Variable': correlations.index,
        'Correlation': correlations.values,
        'Abs_Correlation': np.abs(correlations.values)
    }).sort_values('Abs_Correlation', ascending=False)
    
    return corr_summary.reset_index(drop=True)
