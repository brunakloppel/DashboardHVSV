import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA STREAMLIT
st.set_page_config(layout="wide", page_title="Dashboard Hospital Veterinário")

# Configuração das métricas disponíveis
METRICAS_DISPONIVEIS = {
    'Consultas': [
        'Total Consultas (Dia vs Plantão)',
        'Evolução Temporal Consultas',
        'Comparativo Mensal'
    ],
    'Clientes': [
        'Novos vs Retornantes',
        'Origem Google',
        'Perfil de Clientes'
    ],
    'Faturamento': [
        'Faturamento por Tipo',
        'Ticket Médio',
        'Análise Financeira'
    ]
}

# Configuração dos estilos
st.markdown("""
    <style>
    .graph-explanation {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
    }
    .graph-explanation h4 {
        color: #1f77b4;
        margin-bottom: 10px;
        font-size: 1.1em;
    }
    .graph-explanation ul {
        margin-left: 20px;
        margin-bottom: 10px;
    }
    .graph-explanation li {
        margin-bottom: 5px;
    }
    .graph-explanation p {
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def load_data(excel_file):
    try:
        df_tabela1 = pd.read_excel(excel_file, sheet_name='Tabela1', skiprows=2)
        df_tabela2 = pd.read_excel(excel_file, sheet_name='Tabela2', skiprows=2)
        df_tabela3 = pd.read_excel(excel_file, sheet_name='Tabela3', skiprows=2)
        df_tabela5 = pd.read_excel(excel_file, sheet_name='Tabela5', skiprows=2)
        
        return df_tabela1, df_tabela2, df_tabela3, df_tabela5
    except Exception as e:
        st.error(f'Erro ao carregar dados: {str(e)}')
        return None, None, None, None

    
def criar_grafico_perfil_clientes(df3, unidade_selecionada, ano_selecionado, mes_selecionado):
    """Cria gráfico de Perfil de Clientes"""
    st.markdown("""
    <div class="graph-explanation" style="color: white; background-color: #003366; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
        <h4 style="color: #FFFFFF;">Como interpretar este gráfico:</h4>
        <p>Este gráfico apresenta o perfil dos pacientes atendidos mensalmente.</p>
        <ul>
            <li><strong>Novos:</strong> Total de novos clientes atendidos no período.</li>
            <li><strong>Retornantes:</strong> Clientes que retornaram ao hospital.</li>
            <li><strong>Google Novos:</strong> Novos clientes que chegaram via Google.</li>
            <li><strong>Google Retornantes:</strong> Clientes recorrentes que retornaram via Google.</li>
        </ul>
        <p>Utilize este gráfico para identificar padrões de comportamento e origem dos clientes ao longo dos meses.</p>
    </div>
    """, unsafe_allow_html=True)

    # Filtra os dados para o gráfico
    df_filtered = df3[
        (df3['Unidade'].isin(unidade_selecionada)) &
        (df3['Ano'].isin(ano_selecionado)) &
        (df3['Mês'].isin(mes_selecionado))
    ]
    
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_filtered['Mês'] = pd.Categorical(df_filtered['Mês'], categories=ordem_meses, ordered=True)
    df_filtered = df_filtered.sort_values(['Ano', 'Mês'])
    
    fig = make_subplots(rows=1, cols=1, subplot_titles=["Perfil de Clientes"])
    categorias = ['Novos', 'Retornantes', 'Google Novos', 'Google Retornantes']
    cores = px.colors.qualitative.Set1
    
    for i, cat in enumerate(categorias):
        valores = df_filtered[f'Total Consulta Plantão - {cat}']
        fig.add_trace(
            go.Bar(
                x=df_filtered['Mês'],
                y=valores,
                name=cat,
                marker_color=cores[i]
            )
        )
    
    fig.update_layout(
        title=f"Perfil de Clientes - {', '.join(unidade_selecionada)}",
        xaxis_title="Mês",
        yaxis_title="Total de Clientes",
        barmode="group",
        height=500
    )
    
    return fig



def criar_grafico_consultas(df, tipo, unidade_selecionada, ano_selecionado, mes_selecionado):
    """Cria gráfico baseado no tipo selecionado"""
    df_filtered = df[
        (df['Unidade'].isin(unidade_selecionada)) &
        (df['Ano'].isin(ano_selecionado)) &
        (df['Mês'].isin(mes_selecionado))
    ]
    
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_filtered['Mês'] = pd.Categorical(df_filtered['Mês'], categories=ordem_meses, ordered=True)
    df_filtered = df_filtered.sort_values(['Ano', 'Mês'])
    
    if tipo == 'Total Consultas (Dia vs Plantão)':
        fig = make_subplots(rows=2, cols=1, 
                          subplot_titles=('Consultas Dia', 'Consultas Plantão'),
                          vertical_spacing=0.12)
        
        cores = px.colors.qualitative.Set1
        for i, ano in enumerate(sorted(ano_selecionado)):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            
            # Gráfico de Consultas Dia
            fig.add_trace(
                go.Scatter(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consultas Dia'],
                    name=f'Dia {ano}',
                    mode='lines+markers',
                    line=dict(color=cores[i])
                ),
                row=1, col=1
            )
            
            # Gráfico de Consultas Plantão
            fig.add_trace(
                go.Scatter(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consultas Plantão'],
                    name=f'Plantão {ano}',
                    mode='lines+markers',
                    line=dict(color=cores[i], dash='dash')
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Comparativo: Consultas Dia vs Plantão - {', '.join(unidade_selecionada)}",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
    elif tipo == 'Evolução Temporal Consultas':
        fig = go.Figure()
        
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            df_ano['Total Consultas'] = df_ano['Total Consultas Dia'] + df_ano['Total Consultas Plantão']
            
            fig.add_trace(go.Scatter(
                x=df_ano['Mês'],
                y=df_ano['Total Consultas'],
                name=f'Total {ano}',
                mode='lines+markers'
            ))
            
        fig.update_layout(
            title=f'Evolução do Total de Consultas - {", ".join(unidade_selecionada)}',
            xaxis_title="Mês",
            yaxis_title="Total de Consultas",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
    elif tipo == 'Comparativo Mensal':

        st.info("""
    **Como interpretar este gráfico:**

    Este gráfico apresenta uma análise comparativa mensal das consultas:
    • Barras claras representam consultas durante o dia (2023 e 2024)
    • Barras escuras representam consultas de plantão (2023 e 2024)
    • Os meses estão ordenados de Janeiro a Dezembro
    • Permite comparar simultaneamente:
      - Volume de consultas dia vs plantão
      - Diferenças entre os mesmos meses em anos diferentes
      - Tendências sazonais ao longo do ano

    Use esta visualização para identificar:
    • Meses com maior demanda
    • Proporção entre atendimentos dia e plantão
    • Crescimento ou redução em relação ao ano anterior
    """)
        
        # Criar pivot table para comparativo mensal
        df_pivot = df_filtered.pivot_table(
            values=['Total Consultas Dia', 'Total Consultas Plantão'],
            index='Mês',
            columns='Ano',
            aggfunc='sum'
        ).round(2)
        
        # Calcular variações percentuais
        for coluna in ['Total Consultas Dia', 'Total Consultas Plantão']:
            if len(ano_selecionado) == 2:
                ano_base, ano_comp = sorted(ano_selecionado)
                df_pivot[f'Variação % {coluna}'] = (
                    (df_pivot[(coluna, ano_comp)] - df_pivot[(coluna, ano_base)]) / 
                    df_pivot[(coluna, ano_base)] * 100
                ).round(1)
        
        fig = go.Figure()
        
        # Adicionar barras para cada ano
        for ano in sorted(ano_selecionado):
            fig.add_trace(go.Bar(
                name=f'Dia {ano}',
                x=df_pivot.index,
                y=df_pivot[('Total Consultas Dia', ano)],
                offsetgroup=0
            ))
            fig.add_trace(go.Bar(
                name=f'Plantão {ano}',
                x=df_pivot.index,
                y=df_pivot[('Total Consultas Plantão', ano)],
                offsetgroup=1
            ))
        
        fig.update_layout(
            title=f'Comparativo Mensal de Consultas - {", ".join(unidade_selecionada)}',
            xaxis_title="Mês",
            yaxis_title="Número de Consultas",
            barmode='group',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
    else:
        # Caso default para tipos não reconhecidos
        fig = go.Figure()
        fig.update_layout(
            title="Tipo de gráfico não reconhecido",
            annotations=[dict(
                text="Tipo de gráfico não implementado",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )]
        )
    
    return fig

def criar_grafico_clientes(df2, df3, tipo, unidade_selecionada, ano_selecionado, mes_selecionado):
    st.write("Verificando df3:", df3.head())

    # Debug temporário para ver as colunas disponíveis
    if tipo == 'Perfil de Clientes':
        st.write("DEBUG - Colunas disponíveis em df3:", df3.columns.tolist())
        # Remove as linhas de criação do gráfico por enquanto
        return None
        
    df_filtered = df2[
        (df2['Unidade'].isin(unidade_selecionada)) &
        (df2['Ano'].isin(ano_selecionado)) &
        (df2['Mês'].isin(mes_selecionado))
    ]
    
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_filtered['Mês'] = pd.Categorical(df_filtered['Mês'], categories=ordem_meses, ordered=True)
    df_filtered = df_filtered.sort_values(['Ano', 'Mês'])
    
    fig = None  # Inicializa a figura como None
    
    if tipo == 'Novos vs Retornantes':

        st.info("""
**Como interpretar este gráfico:**

Esta visualização compara dois grupos importantes de clientes:

• Gráfico Superior: Clientes Novos
  - Representa primeiras consultas
  - Indica efetividade da captação de clientes
  - Mostra o crescimento da base de clientes

• Gráfico Inferior: Clientes Retornantes
  - Mostra consultas de clientes que já utilizaram o serviço
  - Indica nível de fidelização
  - Reflete a satisfação com os serviços prestados

Use esta análise para:
• Avaliar estratégias de captação de novos clientes
• Monitorar taxas de retenção
• Identificar períodos de maior atração de novos clientes
• Acompanhar a fidelização da base existente
""")
        
        fig = make_subplots(rows=2, cols=1,
                          subplot_titles=('Clientes Novos', 'Clientes Retornantes'),
                          vertical_spacing=0.12)
        
        cores = px.colors.qualitative.Set1
        for i, ano in enumerate(sorted(ano_selecionado)):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            
            # Gráfico de Novos Clientes
            fig.add_trace(
                go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consulta Dia - Novos'],
                    name=f'Novos {ano}',
                    marker_color=cores[i]
                ),
                row=1, col=1
            )
            
            # Gráfico de Clientes Retornantes
            fig.add_trace(
                go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consulta Dia - Retornantes'],
                    name=f'Retornantes {ano}',
                    marker_color=cores[i],
                    marker_pattern_shape="/"
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Comparativo: Novos vs Retornantes - {', '.join(unidade_selecionada)}",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(title_text="Mês", row=2, col=1)
        fig.update_yaxes(title_text="Número de Clientes", row=1, col=1)
        fig.update_yaxes(title_text="Número de Clientes", row=2, col=1)
        
    elif tipo == 'Origem Google':
        st.info("""
**Como interpretar este gráfico:**

Esta visualização analisa os clientes captados via Google:

• Gráfico Superior: Google Novos
  - Mostra novos clientes que encontraram o hospital via Google
  - Indica efetividade das campanhas digitais
  - Reflete o resultado dos investimentos em marketing digital

• Gráfico Inferior: Google Retornantes
  - Apresenta clientes que retornam através do Google
  - Demonstra a eficácia da presença digital para retenção
  - Indica fidelização através dos canais digitais

Use esta análise para:
• Avaliar o ROI das campanhas do Google
• Identificar períodos de maior conversão digital
• Ajustar estratégias de marketing online
• Otimizar investimentos em mídia digital
""")
        
        fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Clientes Google Novos', 'Clientes Google Retornantes'),
                        vertical_spacing=0.12)
        
        cores = px.colors.qualitative.Set1
        for i, ano in enumerate(sorted(ano_selecionado)):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            
            # Gráfico de Google Novos
            fig.add_trace(
                go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consultas Dia - Google Novos'],
                    name=f'Google Novos {ano}',
                    marker_color=cores[i]
                ),
                row=1, col=1
            )
            
            # Gráfico de Google Retornantes
            fig.add_trace(
                go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano['Total Consulta Dia - Google Retornantes'],
                    name=f'Google Retornantes {ano}',
                    marker_color=cores[i],
                    marker_pattern_shape="/"
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Origem Google - {', '.join(unidade_selecionada)}",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(title_text="Mês", row=2, col=1)
        fig.update_yaxes(title_text="Número de Clientes", row=1, col=1)
        fig.update_yaxes(title_text="Número de Clientes", row=2, col=1)
        
    elif tipo == 'Perfil de Clientes':
        # Filtra dados do df3
        df_filtered_3 = df3[
            (df3['Unidade'].isin(unidade_selecionada)) &
            (df3['Ano'].isin(ano_selecionado)) &
            (df3['Mês'].isin(mes_selecionado))
        ]
        df_filtered_3['Mês'] = pd.Categorical(df_filtered_3['Mês'], categories=ordem_meses, ordered=True)
        df_filtered_3 = df_filtered_3.sort_values(['Ano', 'Mês'])
        
        # Mostra as colunas disponíveis
        st.write("Colunas disponíveis em df3:", df3.columns.tolist())
        
        # Continua com um gráfico simples para não quebrar
        fig = go.Figure()
        fig.update_layout(
            title="Debug - Verificando colunas disponíveis",
            height=400
        )
        
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered_3[df_filtered_3['Ano'] == ano]
            
            fig.add_trace(go.Bar(
                x=df_ano['Mês'],
                y=df_ano['Total Cães'],
                name=f'Cães {ano}',
                marker_color='blue'
            ))
            fig.add_trace(go.Bar(
                x=df_ano['Mês'],
                y=df_ano['Total Gatos'],
                name=f'Gatos {ano}',
                marker_color='orange'
            ))
            fig.add_trace(go.Bar(
                x=df_ano['Mês'],
                y=df_ano['Total Outros'],
                name=f'Outros {ano}',
                marker_color='green'
            ))
            
        fig.update_layout(
            barmode='group',
            title=f'Perfil dos Pacientes por Mês - {", ".join(unidade_selecionada)}',
            xaxis_title="Mês",
            yaxis_title="Número de Pacientes",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
    return fig

def criar_grafico_faturamento(df5, df3, tipo, unidade_selecionada, ano_selecionado, mes_selecionado):
    """Cria gráficos relacionados a faturamento"""
    fig = None
    
    # Filtrando os dados
    df_filtered = df5[
        (df5['Unidade'].isin(unidade_selecionada)) &
        (df5['Ano'].isin(ano_selecionado)) &
        (df5['Mês'].isin(mes_selecionado))
    ]
    
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_filtered['Mês'] = pd.Categorical(df_filtered['Mês'], categories=ordem_meses, ordered=True)
    df_filtered = df_filtered.sort_values(['Ano', 'Mês'])

    # Adicionando explicações sem alterar a lógica dos gráficos
    if tipo == 'Faturamento por Tipo':
        st.markdown("""
        <div class="graph-explanation" style="color: white; background-color: #003366; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
            <h4 style="color: #FFFFFF;">Como interpretar este gráfico:</h4>
            <p>Este gráfico mostra o faturamento total dividido entre Clientes Novos e Retornantes ao longo dos meses.</p>
            <ul>
                <li><strong>Eixo X:</strong> Meses do ano.</li>
                <li><strong>Eixo Y:</strong> Valores de faturamento (em R$).</li>
                <li><strong>Barras:</strong> Comparação entre anos selecionados e categorias de cliente.</li>
            </ul>
            <p>Use este gráfico para analisar o impacto da captação de novos clientes e a fidelização dos clientes existentes.</p>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        for categoria, cor in zip(['Faturamento Clientes Novos', 'Faturamento Clientes Retornantes'], ['#1f77b4', '#ff7f0e']):
            for ano in sorted(ano_selecionado):
                df_ano = df_filtered[df_filtered['Ano'] == ano]
                fig.add_trace(go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano[categoria],
                    name=f"{categoria} - {ano}",
                    marker_color=cor
                ))
        fig.update_layout(
            title=f"Faturamento por Categoria - {', '.join(unidade_selecionada)}",
            xaxis_title="Mês",
            yaxis_title="Faturamento (R$)",
            barmode="group",
            height=500
        )

        
    elif tipo == 'Ticket Médio':
        st.markdown("""
        <div class="graph-explanation" style="color: white; background-color: #003366; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
            <h4 style="color: #FFFFFF;">Como interpretar este gráfico:</h4>
            <p>Este gráfico mostra a evolução do ticket médio (valor médio gasto por cliente) ao longo dos meses.</p>
            <ul>
                <li><strong>Eixo X:</strong> Meses do ano.</li>
                <li><strong>Eixo Y:</strong> Ticket médio (em R$).</li>
                <li><strong>Linha:</strong> Tendência do ticket médio em cada ano selecionado.</li>
            </ul>
            <p>Use este gráfico para monitorar o desempenho financeiro médio por cliente.</p>
        </div>
        """, unsafe_allow_html=True)

        # Código existente para o gráfico
        fig = go.Figure()
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            if 'Faturamento Total' in df_ano.columns and 'Total Clientes' in df_ano.columns:
                df_ano['Ticket Médio'] = df_ano['Faturamento Total'] / df_ano['Total Clientes'].replace(0, np.nan)
            else:
                df_ano['Ticket Médio'] = 0
            
            fig.add_trace(go.Scatter(
                x=df_ano['Mês'],
                y=df_ano['Ticket Médio'],
                name=f'Ticket Médio {ano}',
                mode='lines+markers'
            ))
            
        fig.update_layout(
            title=f'Evolução do Ticket Médio - {", ".join(unidade_selecionada)}',
            xaxis_title="Mês",
            yaxis_title="Ticket Médio (R$)",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(tickformat="R$,.2f")
        )
        
    elif tipo == 'Análise Financeira':
        st.markdown("""
        <div class="graph-explanation" style="color: white; background-color: #003366; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
            <h4 style="color: #FFFFFF;">Como interpretar este gráfico:</h4>
            <p>Este gráfico apresenta uma análise financeira detalhada:</p>
            <ul>
                <li><strong>Evolução do Faturamento:</strong> Tendência ao longo do tempo.</li>
                <li><strong>Distribuição por Unidade:</strong> Proporção do faturamento entre unidades.</li>
                <li><strong>Comparativo Mensal:</strong> Diferença de faturamento entre anos.</li>
                <li><strong>Tendência de Crescimento:</strong> Média móvel do faturamento.</li>
            </ul>
            <p>Use esta análise para identificar padrões e insights financeiros detalhados.</p>
        </div>
        """, unsafe_allow_html=True)

        # Nova implementação para Análise Financeira
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Evolução do Faturamento',
                'Distribuição por Unidade',
                'Comparativo Mensal',
                'Tendência de Crescimento'
            ),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                  [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # 1. Evolução do Faturamento (linha)
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            fig.add_trace(
                go.Scatter(
                    x=df_ano['Mês'],
                    y=df_ano['Faturamento Total'],
                    name=f'Faturamento {ano}',
                    mode='lines+markers'
                ),
                row=1, col=1
            )
        
        # 2. Distribuição por Unidade (pizza)
        fat_por_unidade = df_filtered.groupby('Unidade')['Faturamento Total'].sum()
        fig.add_trace(
            go.Pie(
                labels=fat_por_unidade.index,
                values=fat_por_unidade.values,
                name='Distribuição'
            ),
            row=1, col=2
        )
        
        # 3. Comparativo Mensal (barras)
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            fig.add_trace(
                go.Bar(
                    x=df_ano['Mês'],
                    y=df_ano['Faturamento Total'],
                    name=f'Mensal {ano}'
                ),
                row=2, col=1
            )
        
        # 4. Tendência de Crescimento (linha com média móvel)
        df_tendencia = df_filtered.sort_values(['Ano', 'Mês'])
        df_tendencia['Media_Movel'] = df_tendencia['Faturamento Total'].rolling(window=3).mean()
        
        fig.add_trace(
            go.Scatter(
                x=df_tendencia['Mês'],
                y=df_tendencia['Media_Movel'],
                name='Tendência (MM-3)',
                line=dict(dash='dash')
            ),
            row=2, col=2
        )
        
        # Atualiza o layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Análise Financeira Detalhada - {', '.join(unidade_selecionada)}",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Atualiza formatação dos eixos Y para valores monetários
        fig.update_yaxes(tickformat="R$,.2f", row=1, col=1)
        fig.update_yaxes(tickformat="R$,.2f", row=2, col=1)
        fig.update_yaxes(tickformat="R$,.2f", row=2, col=2)

    elif tipo == 'Faturamento por Categoria':
        fig = go.Figure()
        for categoria, cor in zip(['Faturamento Clientes Novos', 'Faturamento Clientes Retornantes'], ['#1f77b4', '#ff7f0e']):
            fig.add_trace(go.Bar(
                x=df_filtered['Mês'],
                y=df_filtered[categoria],
                name=categoria,
                marker_color=cor
            ))
        
        fig.update_layout(
            title=f"Faturamento por Categoria de Cliente - {', '.join(unidade_selecionada)}",
            xaxis_title="Mês",
            yaxis_title="Faturamento (R$)",
            barmode="group",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )    


    elif tipo == 'Proporção Faturamento':
        total_faturamento = df_filtered[['Faturamento Clientes Novos', 'Faturamento Clientes Retornantes']].sum()
        fig = go.Figure(go.Pie(
            labels=['Clientes Novos', 'Clientes Retornantes'],
            values=total_faturamento,
            hole=0.4
        ))
        fig.update_layout(
            title="Proporção do Faturamento por Tipo de Cliente",
            height=400
        )    

    elif tipo == 'Tendência Anual':
        df_filtered['Faturamento Acumulado'] = df_filtered['Faturamento Total'].cumsum()
        fig = go.Figure()
        for ano in sorted(ano_selecionado):
            df_ano = df_filtered[df_filtered['Ano'] == ano]
            fig.add_trace(go.Scatter(
                x=df_ano['Mês'],
                y=df_ano['Faturamento Acumulado'],
                name=f"{ano} (Acumulado)",
                mode='lines+markers'
            ))
        fig.update_layout(
            title="Tendência de Faturamento Acumulado ao Longo do Ano",
            xaxis_title="Mês",
            yaxis_title="Faturamento Acumulado (R$)",
            height=400
        )
        
        fig.update_layout(
            title="Tendência de Faturamento Acumulado ao Longo do Ano",
            xaxis_title="Mês",
            yaxis_title="Faturamento Acumulado (R$)",
            height=400
        )

    elif tipo == 'Faturamento por Unidade':
        unidade_faturamento = df_filtered.groupby('Unidade')['Faturamento Total'].sum().reset_index()
        fig = px.bar(
            unidade_faturamento,
            x='Unidade',
            y='Faturamento Total',
            title="Faturamento por Unidade",
            text='Faturamento Total',
            color='Unidade'
        )
        fig.update_layout(
            xaxis_title="Unidade",
            yaxis_title="Faturamento Total (R$)",
            height=400
        )
    
    
    return fig



def criar_dashboard():
    
    # Configurações de estilo
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stSelectbox, .stMultiSelect {
            padding: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # # Título com container
    with st.container():
        st.title('Dashboard Interativo - Hospital Veterinário')
        st.markdown("---")

    # Carrega dados
    df1, df2, df3, df5 = load_data('Análise mês Clientes Comparativo anos.xlsx')
    
    if df1 is None:
        return
    
    # Sidebar para filtros e seleção de gráficos
    with st.sidebar:
        st.title("Filtros")
        
        # Filtro de unidade com limite de seleção
        unidades = sorted(df1['Unidade'].unique())
        if len(unidades) > 1:
            unidade_selecionada = st.multiselect(
                'Unidade (máx. 2)',
                unidades,
                default=[unidades[0]],
                max_selections=2
            )
        else:
            unidade_selecionada = unidades
        
        # Filtro de ano com limite de seleção
        anos = sorted(df1['Ano'].unique())
        ano_selecionado = st.multiselect(
            'Ano (máx. 2)',
            anos,
            default=anos[-2:] if len(anos) > 1 else anos,
            max_selections=2
        ) 
    
        
        # Filtro de mês
        ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        mes_selecionado = st.multiselect(
            'Mês',
            ordem_meses,
            default=ordem_meses
        )
        st.write("Meses selecionados:", mes_selecionado)

        
        st.markdown("---")
        st.title("Selecione os Gráficos")
        
        # Seleção de métricas com descrições
        metricas_selecionadas = []
        for categoria, metricas in METRICAS_DISPONIVEIS.items():
            st.subheader(categoria)
            for metrica in metricas:
                if st.checkbox(metrica, help=f"Exibir gráfico de {metrica}"):
                    metricas_selecionadas.append((categoria, metrica))
        
        st.markdown("---")
        cols_por_linha = st.radio(
            "Gráficos por linha",
            [1, 2],
            horizontal=True,
            help="Selecione quantos gráficos deseja ver por linha"
        )

    # Validações de seleção
    if not unidade_selecionada:
        st.warning('Por favor, selecione pelo menos uma unidade.')
        return
    
    if not ano_selecionado:
        st.warning('Por favor, selecione pelo menos um ano.')
        return
    
    if not mes_selecionado:
        st.warning('Por favor, selecione pelo menos um mês.')
        return
    
    # Layout principal
    if not metricas_selecionadas:
        st.info("Selecione os gráficos que deseja visualizar no menu lateral.")
        return
    
    

    # Exibe os indicadores selecionados
    st.markdown("### Indicadores Selecionados")
    col_indicators = st.columns(5)  # Ajustado para 5 colunas

    with col_indicators[0]:
        total_consultas = df1[
            (df1['Unidade'].isin(unidade_selecionada)) &
            (df1['Ano'].isin(ano_selecionado)) &
            (df1['Mês'].isin(mes_selecionado))
        ]['Total Consultas Dia'].sum()
        st.metric("Total de Consultas", f"{total_consultas:,}")

    with col_indicators[1]:
        total_novos = df2[
            (df2['Unidade'].isin(unidade_selecionada)) &
            (df2['Ano'].isin(ano_selecionado)) &
            (df2['Mês'].isin(mes_selecionado))
        ]['Total Consulta Dia - Novos'].sum()
        st.metric("Novos Clientes", f"{total_novos:,}")

    with col_indicators[2]:
        faturamento_total = df5[
            (df5['Unidade'].isin(unidade_selecionada)) &
            (df5['Ano'].isin(ano_selecionado)) &
            (df5['Mês'].isin(mes_selecionado))
        ]['Faturamento Total'].sum()
        st.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")

    with col_indicators[3]:
        ticket_medio = faturamento_total / total_novos if total_novos > 0 else 0
        st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

    with col_indicators[4]:
        # Calcula o faturamento do ano anterior para crescimento
        ano_anterior_total = df5[
            (df5['Unidade'].isin(unidade_selecionada)) &
            (df5['Ano'] == (min(ano_selecionado) - 1)) &  # Ano anterior ao menor ano selecionado
            (df5['Mês'].isin(mes_selecionado))
        ]['Faturamento Total'].sum()
        
        crescimento = ((faturamento_total - ano_anterior_total) / ano_anterior_total) * 100 if ano_anterior_total > 0 else 0
        st.metric("Crescimento (%)", f"{crescimento:.2f}%")

    st.markdown("---")



    # Organiza os gráficos selecionados
    num_metricas = len(metricas_selecionadas)
    for i in range(0, num_metricas, cols_por_linha):
        cols = st.columns(cols_por_linha)
        for j in range(cols_por_linha):
            if i + j < num_metricas:
                categoria, metrica = metricas_selecionadas[i + j]
                with cols[j]:
                    st.markdown(f"#### {metrica}")
                    
                    if categoria == 'Consultas':
                        fig = criar_grafico_consultas(
                            df1, metrica, unidade_selecionada, 
                            ano_selecionado, mes_selecionado
                        )

                    elif categoria == 'Clientes':
                        if metrica == 'Perfil de Clientes':
                            fig = criar_grafico_perfil_clientes(
                                df3, unidade_selecionada, ano_selecionado, mes_selecionado
                            )
                        else:
                            fig = criar_grafico_clientes(
                                df2, df3, metrica, unidade_selecionada,
                                ano_selecionado, mes_selecionado
                            )

                    elif categoria == 'Faturamento':
                        fig = criar_grafico_faturamento(
                            df5,  # DataFrame principal
                            df3,  # DataFrame adicional
                            metrica,
                            unidade_selecionada,
                            ano_selecionado,
                            mes_selecionado  # Este parâmetro estava faltando
                        )
                    
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Gráfico {metrica} não implementado ainda.")

    df_filtered = df5[
    (df5['Unidade'].isin(unidade_selecionada)) &
    (df5['Ano'].isin(ano_selecionado)) &
    (df5['Mês'].isin(mes_selecionado))
]

    # Adicione aqui os destaques automáticos
    st.markdown("### **Destaques Automáticos**")

    # Destaque 1: Mês com maior faturamento
    mes_maior_faturamento = df_filtered.loc[df_filtered['Faturamento Total'].idxmax()]['Mês']
    st.markdown(f"🟢 **Mês com maior faturamento:** {mes_maior_faturamento}")

    # Destaque 2: Ano com maior crescimento
    faturamento_por_ano = df_filtered.groupby('Ano')['Faturamento Total'].sum().to_dict()
    ano_maior_crescimento = max(ano_selecionado, key=lambda ano: faturamento_por_ano.get(ano, 0))
    st.markdown(f"🟢 **Ano com maior crescimento:** {ano_maior_crescimento}")

    # Destaque 3: Categoria com maior faturamento
    total_faturamento = {
        'Faturamento Clientes Novos': df_filtered['Faturamento Clientes Novos'].sum(),
        'Faturamento Clientes Retornantes': df_filtered['Faturamento Clientes Retornantes'].sum()
    }
    categoria_destaque = 'Clientes Novos' if total_faturamento['Faturamento Clientes Novos'] > total_faturamento['Faturamento Clientes Retornantes'] else 'Clientes Retornantes'
    st.markdown(f"🟢 **Categoria de destaque:** {categoria_destaque}")

    # Destaque 4: Proporção do faturamento
    faturamento_novos = total_faturamento['Faturamento Clientes Novos']
    faturamento_retornantes = total_faturamento['Faturamento Clientes Retornantes']
    proporcao_novos = (faturamento_novos / (faturamento_novos + faturamento_retornantes)) * 100
    proporcao_retornantes = 100 - proporcao_novos
    st.markdown(f"🟢 **Proporção do faturamento:** {proporcao_novos:.1f}% Novos / {proporcao_retornantes:.1f}% Retornantes")

                        

        

    # Adiciona rodapé com informações
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p style='color: #666;'>
                Dashboard atualizado em tempo real com dados do Hospital Veterinário.<br>
                Selecione os filtros desejados no menu lateral para personalizar a visualização.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Chamada da função principal
if __name__ == '__main__':
    criar_dashboard()