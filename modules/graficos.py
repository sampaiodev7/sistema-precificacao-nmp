"""
Módulo de Geração de Gráficos
Cria visualizações com Plotly
"""
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

class GeradorGraficos:
    @staticmethod
    def grafico_doughnut_composicao(resultado_markup: Dict):
        labels = [
            'Custo Variável Total',
            'Custo Fixo (sobre Faturamento)',
            'Margem Disponível'
        ]
        valores = [
            resultado_markup['total_cust_var_pct'],
            resultado_markup['pct_cust_fix_sobre_fat'],
            100 - resultado_markup['total_despesas_pct']
        ]
        cores = ['#ef4444', '#3b82f6', '#22c55e']
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=valores,
            hole=0.5,
            marker=dict(colors=cores),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=12)
        )])
        fig.update_layout(
            title={'text': 'Composição Percentual da Precificação',
                   'x': 0.5, 'xanchor': 'center', 'font': {'size': 16, 'family': 'Arial'}},
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=400,
            margin=dict(t=60, b=100, l=20, r=20)
        )
        return fig

    @staticmethod
    def grafico_barras_comparativo(produtos_df: pd.DataFrame, limite: int = 10):
        if produtos_df.empty:
            fig = go.Figure()
            fig.update_layout(title="Nenhum produto cadastrado", height=400)
            return fig
        df_plot = produtos_df.head(limite).copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Custo Total',
            x=df_plot['nome'],
            y=df_plot['custo_total'],
            marker_color='#ef4444',
            text=df_plot['custo_total'].apply(lambda x: f'R$ {x:.2f}'),
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            name='Preço de Venda Final',
            x=df_plot['nome'],
            y=df_plot['preco_final'],
            marker_color='#3b82f6',
            text=df_plot['preco_final'].apply(lambda x: f'R$ {x:.2f}'),
            textposition='outside'
        ))
        fig.update_layout(
            title={'text': 'Custo Total vs. Preço de Venda Final', 'x': 0.5,
                   'xanchor': 'center', 'font': {'size': 16, 'family': 'Arial'}},
            xaxis_title='Produto',
            yaxis_title='Valor (R$)',
            barmode='group', height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(t=100, b=100, l=50, r=50)
        )
        fig.update_xaxes(tickangle=-45)
        return fig

    @staticmethod
    def grafico_margem_categoria(produtos_df: pd.DataFrame):
        if produtos_df.empty or 'categoria' not in produtos_df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados insuficientes para análise por categoria", height=300)
            return fig
        margem_por_cat = produtos_df.groupby('categoria')['margem_liquida_estimada_pct'].mean().reset_index()
        margem_por_cat = margem_por_cat.sort_values('margem_liquida_estimada_pct', ascending=False)
        fig = go.Figure(data=[
            go.Bar(
                x=margem_por_cat['categoria'],
                y=margem_por_cat['margem_liquida_estimada_pct'],
                marker_color='#9333ea',
                text=margem_por_cat['margem_liquida_estimada_pct'].apply(lambda x: f'{x:.2f}%'),
                textposition='outside'
            )
        ])
        fig.update_layout(
            title={'text': 'Margem Líquida Média por Categoria',
                   'x': 0.5, 'xanchor': 'center', 'font': {'size': 14, 'family': 'Arial'}},
            xaxis_title='Categoria', yaxis_title='Margem (%)',
            height=300, margin=dict(t=60, b=80, l=50, r=50)
        )
        return fig
