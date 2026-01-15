"""
Módulo para visualizações avançadas e interativas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from typing import Dict, List, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

from ..utils.helpers import save_figure, setup_plotting_style
from ..utils.config import get_results_path


class AdvancedVisualizer:
    """
    Classe para visualizações avançadas e análises específicas para hipertensão.
    """
    
    def __init__(self):
        """
        Inicializa o visualizador avançado.
        """
        setup_plotting_style()
        
        # Configurações de cores
        self.colors = {
            'low_risk': '#4CAF50',
            'high_risk': '#F44336',
            'primary': '#1976D2',
            'secondary': '#FF9800',
            'accent': '#9C27B0'
        }
        
        # Configurações para Plotly
        self.plotly_template = 'plotly_white'
    
    def create_medical_dashboard(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> go.Figure:
        """
        Cria dashboard médico interativo específico para hipertensão.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Figura Plotly do dashboard
        """
        # Criar subplots
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'Distribuição de Pressão Arterial', 'IMC vs Idade por Risco',
                'Distribuição de Classes', 'Pressão por Faixa Etária',
                'Fatores de Risco Cardiovascular', 'Correlação: Pressão vs Glicose',
                'Distribuição de Colesterol', 'Análise de Medicamentos',
                'Frequência Cardíaca vs Risco'
            ],
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "violin"}, {"type": "bar"}, {"type": "scatter"}],
                [{"type": "histogram"}, {"type": "bar"}, {"type": "box"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # 1. Scatter Pressão Sistólica vs Diastólica
        for risk in [0, 1]:
            risk_data = df[df[target_col] == risk]
            color = self.colors['low_risk'] if risk == 0 else self.colors['high_risk']
            name = 'Baixo Risco' if risk == 0 else 'Alto Risco'
            
            fig.add_trace(
                go.Scatter(
                    x=risk_data['pressao_sistolica'],
                    y=risk_data['pressao_diastolica'],
                    mode='markers',
                    name=name,
                    marker=dict(color=color, size=5, opacity=0.6),
                    showlegend=True if risk == 0 else False
                ),
                row=1, col=1
            )
        
        # 2. IMC vs Idade
        fig.add_trace(
            go.Scatter(
                x=df['idade'],
                y=df['imc'],
                mode='markers',
                marker=dict(
                    color=df[target_col],
                    colorscale=[[0, self.colors['low_risk']], [1, self.colors['high_risk']]],
                    size=8,
                    opacity=0.7,
                    colorbar=dict(title="Risco", x=0.65, y=0.85)
                ),
                text=df[target_col].map({0: 'Baixo Risco', 1: 'Alto Risco'}),
                hovertemplate='Idade: %{x}<br>IMC: %{y:.1f}<br>%{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Distribuição de Classes
        risk_counts = df[target_col].value_counts()
        fig.add_trace(
            go.Bar(
                x=['Baixo Risco', 'Alto Risco'],
                y=[risk_counts[0], risk_counts[1]],
                marker_color=[self.colors['low_risk'], self.colors['high_risk']],
                text=[f'{risk_counts[0]:,}', f'{risk_counts[1]:,}'],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=3
        )
        
        # 4. Pressão por Faixa Etária
        df_temp = df.copy()
        df_temp['faixa_etaria'] = pd.cut(df_temp['idade'], 
                                       bins=[30, 40, 50, 60, 70], 
                                       labels=['30-40', '40-50', '50-60', '60-70'])
        
        for faixa in df_temp['faixa_etaria'].cat.categories:
            faixa_data = df_temp[df_temp['faixa_etaria'] == faixa]
            fig.add_trace(
                go.Violin(
                    y=faixa_data['pressao_sistolica'],
                    name=str(faixa),
                    box_visible=True,
                    meanline_visible=True,
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # 5. Fatores de Risco
        fatores = ['diabetes', 'fumante_atualmente', 'medicamento_pressao']
        risk_by_factor = []
        
        for fator in fatores:
            if fator in df.columns:
                risk_pct = df[df[fator] == 1][target_col].mean() * 100
                risk_by_factor.append(risk_pct)
            else:
                risk_by_factor.append(0)
        
        fig.add_trace(
            go.Bar(
                x=['Diabetes', 'Fumante', 'Med. Pressão'],
                y=risk_by_factor,
                marker_color=self.colors['accent'],
                text=[f'{x:.1f}%' for x in risk_by_factor],
                textposition='auto',
                showlegend=False
            ),
            row=2, col=2
        )
        
        # 6. Correlação Pressão vs Glicose
        fig.add_trace(
            go.Scatter(
                x=df['pressao_sistolica'],
                y=df['glicose'],
                mode='markers',
                marker=dict(
                    color=df[target_col],
                    colorscale=[[0, self.colors['low_risk']], [1, self.colors['high_risk']]],
                    size=6,
                    opacity=0.6
                ),
                showlegend=False
            ),
            row=2, col=3
        )
        
        # 7. Distribuição de Colesterol
        fig.add_trace(
            go.Histogram(
                x=df[df[target_col] == 0]['colesterol_total'],
                name='Baixo Risco',
                opacity=0.7,
                marker_color=self.colors['low_risk'],
                showlegend=False
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Histogram(
                x=df[df[target_col] == 1]['colesterol_total'],
                name='Alto Risco',
                opacity=0.7,
                marker_color=self.colors['high_risk'],
                showlegend=False
            ),
            row=3, col=1
        )
        
        # 8. Análise de Medicamentos
        if 'medicamento_pressao' in df.columns:
            med_analysis = df.groupby(['medicamento_pressao', target_col]).size().reset_index(name='count')
            med_labels = ['Sem Medicamento', 'Com Medicamento']
            
            for i, med_status in enumerate([0, 1]):
                med_data = med_analysis[med_analysis['medicamento_pressao'] == med_status]
                if len(med_data) > 0:
                    fig.add_trace(
                        go.Bar(
                            x=[med_labels[i]],
                            y=med_data['count'].sum(),
                            marker_color=self.colors['primary'] if med_status == 0 else self.colors['secondary'],
                            showlegend=False
                        ),
                        row=3, col=2
                    )
        
        # 9. Box plot Frequência Cardíaca
        for risk in [0, 1]:
            risk_data = df[df[target_col] == risk]
            name = 'Baixo Risco' if risk == 0 else 'Alto Risco'
            color = self.colors['low_risk'] if risk == 0 else self.colors['high_risk']
            
            fig.add_trace(
                go.Box(
                    y=risk_data['frequencia_cardiaca'],
                    name=name,
                    marker_color=color,
                    showlegend=False
                ),
                row=3, col=3
            )
        
        # Atualizar layout
        fig.update_layout(
            height=1200,
            title_text="Dashboard Médico - Análise de Fatores de Risco para Hipertensão",
            title_x=0.5,
            title_font_size=20,
            template=self.plotly_template,
            showlegend=True
        )
        
        # Atualizar eixos
        fig.update_xaxes(title_text="Pressão Sistólica (mmHg)", row=1, col=1)
        fig.update_yaxes(title_text="Pressão Diastólica (mmHg)", row=1, col=1)
        
        fig.update_xaxes(title_text="Idade (anos)", row=1, col=2)
        fig.update_yaxes(title_text="IMC (kg/m²)", row=1, col=2)
        
        fig.update_yaxes(title_text="Número de Pacientes", row=1, col=3)
        
        fig.update_yaxes(title_text="Pressão Sistólica (mmHg)", row=2, col=1)
        fig.update_yaxes(title_text="% Alto Risco", row=2, col=2)
        
        fig.update_xaxes(title_text="Pressão Sistólica (mmHg)", row=2, col=3)
        fig.update_yaxes(title_text="Glicose (mg/dL)", row=2, col=3)
        
        fig.update_xaxes(title_text="Colesterol Total (mg/dL)", row=3, col=1)
        fig.update_yaxes(title_text="Frequência", row=3, col=1)
        
        fig.update_yaxes(title_text="Frequência Cardíaca (bpm)", row=3, col=3)
        
        return fig
    
    def create_correlation_network(self, df: pd.DataFrame, threshold: float = 0.3) -> go.Figure:
        """
        Cria visualização de rede de correlações.
        
        Args:
            df: DataFrame com dados
            threshold: Threshold para mostrar correlações
            
        Returns:
            Figura Plotly da rede
        """
        # Calcular matriz de correlação
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix = df[numeric_cols].corr()
        
        # Preparar dados para a rede
        nodes = []
        edges = []
        
        # Criar nós
        for i, col in enumerate(numeric_cols):
            nodes.append({
                'id': i,
                'name': col.replace('_', ' ').title(),
                'x': np.cos(2 * np.pi * i / len(numeric_cols)),
                'y': np.sin(2 * np.pi * i / len(numeric_cols))
            })
        
        # Criar arestas (correlações significativas)
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Evitar duplicatas
                    corr_val = corr_matrix.loc[col1, col2]
                    if abs(corr_val) >= threshold:
                        edges.append({
                            'x0': nodes[i]['x'], 'y0': nodes[i]['y'],
                            'x1': nodes[j]['x'], 'y1': nodes[j]['y'],
                            'correlation': corr_val
                        })
        
        # Criar figura
        fig = go.Figure()
        
        # Adicionar arestas
        for edge in edges:
            color_intensity = abs(edge['correlation'])
            line_color = 'red' if edge['correlation'] < 0 else 'blue'
            
            fig.add_trace(go.Scatter(
                x=[edge['x0'], edge['x1'], None],
                y=[edge['y0'], edge['y1'], None],
                mode='lines',
                line=dict(
                    color=line_color,
                    width=color_intensity * 5
                ),
                opacity=0.6,
                hoverinfo='skip',
                showlegend=False
            ))
        
        # Adicionar nós
        node_trace = go.Scatter(
            x=[node['x'] for node in nodes],
            y=[node['y'] for node in nodes],
            mode='markers+text',
            text=[node['name'] for node in nodes],
            textposition='middle center',
            marker=dict(
                size=30,
                color=self.colors['primary'],
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{text}</b><extra></extra>',
            showlegend=False
        )
        
        fig.add_trace(node_trace)
        
        # Layout
        fig.update_layout(
            title="Rede de Correlações entre Variáveis",
            title_x=0.5,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text=f"Threshold: {threshold} | Azul: Correlação Positiva | Vermelho: Correlação Negativa",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template=self.plotly_template
        )
        
        return fig
    
    def create_risk_assessment_chart(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> go.Figure:
        """
        Cria gráfico de avaliação de risco médico.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Figura Plotly do assessment
        """
        # Definir categorias de risco baseadas em diretrizes médicas
        risk_categories = {
            'Pressão Arterial': {
                'Normal': (df['pressao_sistolica'] < 120) & (df['pressao_diastolica'] < 80),
                'Elevada': (df['pressao_sistolica'].between(120, 129)) & (df['pressao_diastolica'] < 80),
                'Hipertensão Estágio 1': (df['pressao_sistolica'].between(130, 139)) | (df['pressao_diastolica'].between(80, 89)),
                'Hipertensão Estágio 2': (df['pressao_sistolica'] >= 140) | (df['pressao_diastolica'] >= 90)
            },
            'IMC': {
                'Baixo Peso': df['imc'] < 18.5,
                'Normal': df['imc'].between(18.5, 24.9),
                'Sobrepeso': df['imc'].between(25, 29.9),
                'Obesidade': df['imc'] >= 30
            },
            'Colesterol': {
                'Desejável': df['colesterol_total'] < 200,
                'Limítrofe': df['colesterol_total'].between(200, 239),
                'Alto': df['colesterol_total'] >= 240
            }
        }
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Distribuição de Risco por Pressão Arterial',
                'Distribuição de Risco por IMC',
                'Distribuição de Risco por Colesterol',
                'Score de Risco Combinado'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Função para calcular risco por categoria
        def calc_risk_by_category(category_dict):
            results = {}
            for cat_name, condition in category_dict.items():
                if condition.sum() > 0:
                    risk_pct = df[condition][target_col].mean() * 100
                    count = condition.sum()
                    results[cat_name] = {'risk_pct': risk_pct, 'count': count}
            return results
        
        # Posições dos gráficos
        positions = [(1, 1), (1, 2), (2, 1)]
        
        for i, (category, conditions) in enumerate(risk_categories.items()):
            if i < 3:  # Primeiros 3 gráficos
                risk_data = calc_risk_by_category(conditions)
                
                categories = list(risk_data.keys())
                risk_percentages = [risk_data[cat]['risk_pct'] for cat in categories]
                counts = [risk_data[cat]['count'] for cat in categories]
                
                # Cores baseadas no nível de risco
                colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336'][:len(categories)]
                
                fig.add_trace(
                    go.Bar(
                        x=categories,
                        y=risk_percentages,
                        text=[f'{pct:.1f}%<br>({count} pacientes)' 
                              for pct, count in zip(risk_percentages, counts)],
                        textposition='auto',
                        marker_color=colors,
                        showlegend=False,
                        hovertemplate='<b>%{x}</b><br>Risco: %{y:.1f}%<extra></extra>'
                    ),
                    row=positions[i][0], col=positions[i][1]
                )
        
        # 4. Score de Risco Combinado
        df_temp = df.copy()
        
        # Calcular score de risco simples
        risk_score = 0
        
        # Pontos por pressão arterial
        risk_score += np.where(df_temp['pressao_sistolica'] >= 140, 3,
                              np.where(df_temp['pressao_sistolica'] >= 130, 2,
                                      np.where(df_temp['pressao_sistolica'] >= 120, 1, 0)))
        
        # Pontos por IMC
        risk_score += np.where(df_temp['imc'] >= 30, 2,
                              np.where(df_temp['imc'] >= 25, 1, 0))
        
        # Pontos por idade
        risk_score += np.where(df_temp['idade'] >= 60, 2,
                              np.where(df_temp['idade'] >= 45, 1, 0))
        
        # Pontos por fatores adicionais
        if 'diabetes' in df_temp.columns:
            risk_score += df_temp['diabetes'] * 2
        if 'fumante_atualmente' in df_temp.columns:
            risk_score += df_temp['fumante_atualmente'] * 1
        
        df_temp['risk_score'] = risk_score
        
        # Categorizar score
        df_temp['risk_category'] = pd.cut(df_temp['risk_score'],
                                         bins=[-1, 2, 4, 6, 15],
                                         labels=['Baixo', 'Moderado', 'Alto', 'Muito Alto'])
        
        # Calcular risco por score
        score_risk = df_temp.groupby('risk_category')[target_col].agg(['mean', 'count']).reset_index()
        score_risk['risk_pct'] = score_risk['mean'] * 100
        
        # Cores para diferentes níveis de score
        score_colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
        
        fig.add_trace(
            go.Bar(
                x=score_risk['risk_category'],
                y=score_risk['risk_pct'],
                text=[f'{pct:.1f}%<br>({count} pacientes)' 
                      for pct, count in zip(score_risk['risk_pct'], score_risk['count'])],
                textposition='auto',
                marker_color=score_colors,
                showlegend=False,
                hovertemplate='<b>Risco %{x}</b><br>Hipertensão: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Atualizar layout
        fig.update_layout(
            height=800,
            title_text="Avaliação de Risco Cardiovascular - Análise por Categorias Médicas",
            title_x=0.5,
            title_font_size=18,
            template=self.plotly_template
        )
        
        # Atualizar eixos
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_yaxes(title_text="% Risco de Hipertensão", row=i, col=j)
        
        return fig
    
    def create_temporal_analysis(self, df: pd.DataFrame, target_col: str = 'risco_hipertensao') -> go.Figure:
        """
        Cria análise temporal por faixas etárias.
        
        Args:
            df: DataFrame com dados
            target_col: Nome da coluna target
            
        Returns:
            Figura Plotly da análise temporal
        """
        # Criar faixas etárias
        df_temp = df.copy()
        df_temp['faixa_etaria'] = pd.cut(df_temp['idade'],
                                        bins=[30, 35, 40, 45, 50, 55, 60, 65, 70],
                                        labels=['30-35', '35-40', '40-45', '45-50', 
                                               '50-55', '55-60', '60-65', '65-70'])
        
        # Análise por faixa etária
        age_analysis = df_temp.groupby('faixa_etaria').agg({
            target_col: ['mean', 'count'],
            'pressao_sistolica': 'mean',
            'pressao_diastolica': 'mean',
            'imc': 'mean',
            'colesterol_total': 'mean'
        }).reset_index()
        
        # Simplificar nomes das colunas
        age_analysis.columns = ['faixa_etaria', 'risk_pct', 'count', 'sys_bp', 'dia_bp', 'bmi', 'chol']
        age_analysis['risk_pct'] *= 100
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Prevalência de Hipertensão por Idade',
                'Evolução da Pressão Arterial',
                'IMC ao Longo da Idade',
                'Colesterol por Faixa Etária'
            ],
            specs=[[{"secondary_y": True}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Prevalência por idade
        fig.add_trace(
            go.Bar(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['count'],
                name='Número de Pacientes',
                marker_color='lightblue',
                opacity=0.7,
                yaxis='y',
                offsetgroup=1
            ),
            row=1, col=1, secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['risk_pct'],
                mode='lines+markers',
                name='% Risco Hipertensão',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ),
            row=1, col=1, secondary_y=True
        )
        
        # 2. Pressão arterial
        fig.add_trace(
            go.Scatter(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['sys_bp'],
                mode='lines+markers',
                name='Pressão Sistólica',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['dia_bp'],
                mode='lines+markers',
                name='Pressão Diastólica',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # 3. IMC por idade
        fig.add_trace(
            go.Scatter(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['bmi'],
                mode='lines+markers',
                name='IMC Médio',
                line=dict(color='green', width=3),
                marker=dict(size=8),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        # Linha de referência para sobrepeso
        fig.add_hline(y=25, line_dash="dash", line_color="orange", 
                     annotation_text="Sobrepeso (IMC ≥ 25)", row=2, col=1)
        
        # 4. Colesterol por idade
        fig.add_trace(
            go.Scatter(
                x=age_analysis['faixa_etaria'],
                y=age_analysis['chol'],
                mode='lines+markers',
                name='Colesterol Médio',
                line=dict(color='purple', width=3),
                marker=dict(size=8),
                fill='tozeroy'
            ),
            row=2, col=2
        )
        
        # Linha de referência para colesterol alto
        fig.add_hline(y=200, line_dash="dash", line_color="red",
                     annotation_text="Limítrofe (≥ 200 mg/dL)", row=2, col=2)
        
        # Atualizar layout
        fig.update_layout(
            height=800,
            title_text="Análise Temporal - Evolução dos Fatores de Risco por Idade",
            title_x=0.5,
            title_font_size=18,
            template=self.plotly_template,
            showlegend=True
        )
        
        # Atualizar eixos
        fig.update_xaxes(title_text="Faixa Etária (anos)", row=1, col=1)
        fig.update_yaxes(title_text="Número de Pacientes", secondary_y=False, row=1, col=1)
        fig.update_yaxes(title_text="% Risco Hipertensão", secondary_y=True, row=1, col=1)
        
        fig.update_xaxes(title_text="Faixa Etária (anos)", row=1, col=2)
        fig.update_yaxes(title_text="Pressão Arterial (mmHg)", row=1, col=2)
        
        fig.update_xaxes(title_text="Faixa Etária (anos)", row=2, col=1)
        fig.update_yaxes(title_text="IMC (kg/m²)", row=2, col=1)
        
        fig.update_xaxes(title_text="Faixa Etária (anos)", row=2, col=2)
        fig.update_yaxes(title_text="Colesterol Total (mg/dL)", row=2, col=2)
        
        return fig
    
    def save_interactive_dashboard(self, fig: go.Figure, name: str, subfolder: str = "eda"):
        """
        Salva dashboard interativo.
        
        Args:
            fig: Figura Plotly
            name: Nome do arquivo
            subfolder: Subpasta para salvar
        """
        save_path = get_results_path("figures") / subfolder
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar como HTML
        html_path = save_path / f"{name}.html"
        fig.write_html(str(html_path))
        
        # Salvar como imagem estática também
        img_path = save_path / f"{name}.png"
        fig.write_image(str(img_path), width=1200, height=800, scale=2)
        
        print(f"📊 Dashboard salvo em: {html_path}")
        print(f"🖼️  Imagem salva em: {img_path}")


def create_advanced_visualizer() -> AdvancedVisualizer:
    """
    Função de conveniência para criar visualizador avançado.
    
    Returns:
        Instância do AdvancedVisualizer
    """
    return AdvancedVisualizer()


if __name__ == "__main__":
    print("🧪 Testando módulo AdvancedVisualizer...")
    
    # Criar dados de teste
    np.random.seed(42)
    n_samples = 1000
    
    test_data = pd.DataFrame({
        'idade': np.random.randint(30, 70, n_samples),
        'pressao_sistolica': np.random.normal(130, 20, n_samples),
        'pressao_diastolica': np.random.normal(85, 15, n_samples),
        'imc': np.random.normal(25, 5, n_samples),
        'colesterol_total': np.random.normal(220, 40, n_samples),
        'frequencia_cardiaca': np.random.normal(75, 12, n_samples),
        'glicose': np.random.normal(85, 20, n_samples),
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'fumante_atualmente': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'medicamento_pressao': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'risco_hipertensao': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    # Testar visualizador
    viz = AdvancedVisualizer()
    
    print("✅ Teste concluído!")
    print("📊 AdvancedVisualizer pronto para uso")