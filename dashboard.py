import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def criar_dashboard():
    st.set_page_config(layout="wide", page_title="Dashboard Hospital Veterinário Santa Vida")
    st.title('Dashboard Hospital Veterinário Santa Vida')

    # Carrega o arquivo Excel
    excel_file = 'Análise mês Clientes Comparativo anos.xlsx'
    try:
        excel = pd.ExcelFile(excel_file)
        todas_abas = excel.sheet_names
        
        # Sidebar para navegação
        st.sidebar.title('Navegação')
        aba_selecionada = st.sidebar.selectbox('Selecione a análise:', todas_abas)
        
        # Lê os dados da aba selecionada
        df = pd.read_excel(excel_file, sheet_name=aba_selecionada, skiprows=2)
        
        # Adiciona estas linhas para debug
        st.write("Primeiras linhas do DataFrame:")
        st.write(df.head())
        st.write("Colunas disponíveis:", df.columns.tolist())

        # Tenta corrigir o nome da coluna se necessário
        for col in df.columns:
            if 'UNIDADE' in col.upper() or 'Unidade' in col:
                df = df.rename(columns={col: 'Unidade'})
                break

        # Remove linhas vazias
        df = df.dropna(how='all')

        # Filtros globais
        col1, col2, col3 = st.columns(3)
        with col1:
            unidades = sorted(df['Unidade'].unique())
            unidade_selecionada = st.multiselect('Unidade', unidades, default=unidades)
        with col2:
            anos = sorted(df['Ano'].unique())
            ano_selecionado = st.multiselect('Ano', anos, default=anos)
        with col3:
            meses = sorted(df['Mês'].unique())
            mes_selecionado = st.multiselect('Mês', meses, default=meses)

        # Filtra os dados
        df_filtrado = df[
            (df['Unidade'].isin(unidade_selecionada)) &
            (df['Ano'].isin(ano_selecionado)) &
            (df['Mês'].isin(mes_selecionado))
        ]

        
        # Visualizações específicas para cada aba
        if aba_selecionada == "Tabela1":
                st.subheader("Análise de Consultas Dia e Plantão - Comparativo por Unidade")
                
                # Seletor de unidade para análise detalhada
                unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
                
                # Filtra dados da unidade selecionada
                df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
                
                # Gráficos comparativos para a unidade selecionada
                st.subheader(f"Análise Detalhada - {unidade_analise}")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Gráfico de Consultas Dia
                    fig_dia = px.line(
                        df_unidade,
                        x='Mês',
                        y='Total Consultas Dia',
                        color='Ano',
                        title=f'Evolução Consultas Dia - {unidade_analise}',
                        markers=True
                    )
                    fig_dia.add_bar(
                        x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                        y=df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Dia'],
                        name='2024',
                        opacity=0.3
                    )
                    st.plotly_chart(fig_dia, use_container_width=True)
                    
                    # Métricas de Consultas Dia
                    total_dia_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consultas Dia'].sum()
                    total_dia_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Dia'].sum()
                    variacao_dia = ((total_dia_2024 - total_dia_2023) / total_dia_2023 * 100) if total_dia_2023 > 0 else 0
                    st.metric(
                        "Variação Consultas Dia (2023 vs 2024)", 
                        f"{variacao_dia:.1f}%",
                        delta=f"{total_dia_2024 - total_dia_2023:.0f} consultas"
                    )
                
                with col2:
                    # Gráfico de Consultas Plantão
                    fig_plantao = px.line(
                        df_unidade,
                        x='Mês',
                        y='Total Consultas Plantão',
                        color='Ano',
                        title=f'Evolução Consultas Plantão - {unidade_analise}',
                        markers=True
                    )
                    fig_plantao.add_bar(
                        x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                        y=df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Plantão'],
                        name='2024',
                        opacity=0.3
                    )
                    st.plotly_chart(fig_plantao, use_container_width=True)
                    
                    # Métricas de Consultas Plantão
                    total_plantao_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consultas Plantão'].sum()
                    total_plantao_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Plantão'].sum()
                    variacao_plantao = ((total_plantao_2024 - total_plantao_2023) / total_plantao_2023 * 100) if total_plantao_2023 > 0 else 0
                    st.metric(
                        "Variação Consultas Plantão (2023 vs 2024)", 
                        f"{variacao_plantao:.1f}%",
                        delta=f"{total_plantao_2024 - total_plantao_2023:.0f} consultas"
                    )

                # Tabela de comparativo mensal
                st.subheader("Comparativo Mensal Detalhado")
                df_comp = df_unidade.pivot_table(
                    values=['Total Consultas Dia', 'Total Consultas Plantão'],
                    index='Mês',
                    columns='Ano',
                    aggfunc='sum'
                ).round(2)
                
                # Calculando variações percentuais
                df_comp['Variação % Dia'] = ((df_comp[('Total Consultas Dia', 2024)] - 
                                            df_comp[('Total Consultas Dia', 2023)]) / 
                                            df_comp[('Total Consultas Dia', 2023)] * 100).round(1)
                df_comp['Variação % Plantão'] = ((df_comp[('Total Consultas Plantão', 2024)] - 
                                                df_comp[('Total Consultas Plantão', 2023)]) / 
                                                df_comp[('Total Consultas Plantão', 2023)] * 100).round(1)
                
                st.dataframe(df_comp)

                # Resumo geral da unidade
                st.subheader("Resumo Geral da Unidade")
                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "Média Mensal Consultas Dia 2024", 
                    f"{df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Dia'].mean():.0f}"
                )
                col2.metric(
                    "Média Mensal Consultas Plantão 2024",
                    f"{df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Plantão'].mean():.0f}"
                )
                col3.metric(
                    "Proporção Dia/Plantão 2024",
                    f"{(df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Dia'].sum() / df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Plantão'].sum()):.1f}"
                )

        elif aba_selecionada == "Tabela2":
            st.subheader("Análise de Consultas Dia - Novos vs Retornantes - Comparativo por Unidade")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Consultas Regulares
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de Clientes Novos
                fig_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Dia - Novos',
                    color='Ano',
                    title=f'Evolução Consultas Dia (Novos) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_novos, use_container_width=True)
                
                # Métricas de Clientes Novos
                total_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Dia - Novos'].sum()
                total_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Dia - Novos'].sum()
                variacao_novos = ((total_novos_2024 - total_novos_2023) / total_novos_2023 * 100) if total_novos_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Novos (2023 vs 2024)", 
                    f"{variacao_novos:.1f}%",
                    delta=f"{total_novos_2024 - total_novos_2023:.0f} consultas"
                )
            
            with col2:
                # Gráfico de Clientes Retornantes
                fig_retornantes = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Dia - Retornantes',
                    color='Ano',
                    title=f'Evolução Consultas Dia (Retornantes) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_retornantes, use_container_width=True)
                
                # Métricas de Clientes Retornantes
                total_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Dia - Retornantes'].sum()
                total_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Dia - Retornantes'].sum()
                variacao_ret = ((total_ret_2024 - total_ret_2023) / total_ret_2023 * 100) if total_ret_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Retornantes (2023 vs 2024)", 
                    f"{variacao_ret:.1f}%",
                    delta=f"{total_ret_2024 - total_ret_2023:.0f} consultas"
                )

            # Consultas via Google
            st.subheader("Análise de Consultas via Google")
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de Clientes Google Novos
                fig_google_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consultas Dia - Google Novos',
                    color='Ano',
                    title=f'Evolução Consultas Google (Novos) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_google_novos, use_container_width=True)
                
                # Métricas Google Novos
                total_google_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consultas Dia - Google Novos'].sum()
                total_google_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Dia - Google Novos'].sum()
                variacao_google_novos = ((total_google_novos_2024 - total_google_novos_2023) / total_google_novos_2023 * 100) if total_google_novos_2023 > 0 else 0
                st.metric(
                    "Variação Google Novos (2023 vs 2024)", 
                    f"{variacao_google_novos:.1f}%",
                    delta=f"{total_google_novos_2024 - total_google_novos_2023:.0f} consultas"
                )
            
            with col2:
                # Gráfico de Clientes Google Retornantes
                fig_google_ret = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Dia - Google Retornantes',
                    color='Ano',
                    title=f'Evolução Consultas Google (Retornantes) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_google_ret, use_container_width=True)
                
                # Métricas Google Retornantes
                total_google_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Dia - Google Retornantes'].sum()
                total_google_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Dia - Google Retornantes'].sum()
                variacao_google_ret = ((total_google_ret_2024 - total_google_ret_2023) / total_google_ret_2023 * 100) if total_google_ret_2023 > 0 else 0
                st.metric(
                    "Variação Google Retornantes (2023 vs 2024)", 
                    f"{variacao_google_ret:.1f}%",
                    delta=f"{total_google_ret_2024 - total_google_ret_2023:.0f} consultas"
                )

            # Análise de Faturamento
            st.subheader("Análise de Faturamento")
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Novos
                fig_fat_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consulta Dia - Novos',
                    color='Ano',
                    title=f'Faturamento Clientes Novos - {unidade_analise}',
                    markers=True
                )
                fig_fat_novos.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_novos, use_container_width=True)
            
            with col2:
                # Faturamento Retornantes
                fig_fat_ret = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consulta Dia - Retornantes',
                    color='Ano',
                    title=f'Faturamento Clientes Retornantes - {unidade_analise}',
                    markers=True
                )
                fig_fat_ret.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_ret, use_container_width=True)

            # Google separado
            st.subheader("Análise de Faturamento - Google")
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Google Novos
                fig_fat_google_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consultas Dia - Google Novos',
                    color='Ano',
                    title=f'Faturamento Google Novos - {unidade_analise}',
                    markers=True
                )
                fig_fat_google_novos.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_google_novos, use_container_width=True)
            
            with col2:
                # Faturamento Google Retornantes
                fig_fat_google_ret = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consulta Dia - Google Retornantes',
                    color='Ano',
                    title=f'Faturamento Google Retornantes - {unidade_analise}',
                    markers=True
                )
                fig_fat_google_ret.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_google_ret, use_container_width=True)

        elif aba_selecionada == "Tabela3":
            st.subheader("Análise de Consultas Plantão - Novos vs Retornantes")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Consultas Plantão
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de Clientes Novos
                fig_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão - Novos',
                    color='Ano',
                    title=f'Evolução Consultas Plantão (Novos) - {unidade_analise}',
                    markers=True
                )
                fig_novos.add_bar(
                    x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                    y=df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Novos'],
                    name='2024',
                    opacity=0.3
                )
                st.plotly_chart(fig_novos, use_container_width=True)
                
                # Métricas de Clientes Novos
                total_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão - Novos'].sum()
                total_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Novos'].sum()
                variacao_novos = ((total_novos_2024 - total_novos_2023) / total_novos_2023 * 100) if total_novos_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Novos (2023 vs 2024)", 
                    f"{variacao_novos:.1f}%",
                    delta=f"{total_novos_2024 - total_novos_2023:.0f} consultas"
                )
            
            with col2:
                # Gráfico de Clientes Retornantes
                fig_retornantes = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão - Retornantes',
                    color='Ano',
                    title=f'Evolução Consultas Plantão (Retornantes) - {unidade_analise}',
                    markers=True
                )
                fig_retornantes.add_bar(
                    x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                    y=df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Retornantes'],
                    name='2024',
                    opacity=0.3
                )
                st.plotly_chart(fig_retornantes, use_container_width=True)
                
                # Métricas de Clientes Retornantes
                total_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão - Retornantes'].sum()
                total_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Retornantes'].sum()
                variacao_ret = ((total_ret_2024 - total_ret_2023) / total_ret_2023 * 100) if total_ret_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Retornantes (2023 vs 2024)", 
                    f"{variacao_ret:.1f}%",
                    delta=f"{total_ret_2024 - total_ret_2023:.0f} consultas"
                )

            # Análise de Faturamento
            st.subheader("Análise de Faturamento Plantão")
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Novos
                fig_fat_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consulta Plantão - Novos',
                    color='Ano',
                    title=f'Faturamento Plantão Novos - {unidade_analise}',
                    markers=True
                )
                fig_fat_novos.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_novos, use_container_width=True)
                
                # Métricas de Faturamento Novos
                fat_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Líquido Total Consulta Plantão - Novos'].sum()
                fat_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Líquido Total Consulta Plantão - Novos'].sum()
                var_fat_novos = ((fat_novos_2024 - fat_novos_2023) / fat_novos_2023 * 100) if fat_novos_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Novos (2023 vs 2024)", 
                    f"{var_fat_novos:.1f}%",
                    delta=f"R$ {fat_novos_2024 - fat_novos_2023:,.2f}"
                )
            
            with col2:
                # Faturamento Retornantes
                fig_fat_ret = px.line(
                    df_unidade,
                    x='Mês',
                    y='Faturamento Líquido Total Consulta Plantão - Retornantes',
                    color='Ano',
                    title=f'Faturamento Plantão Retornantes - {unidade_analise}',
                    markers=True
                )
                fig_fat_ret.update_layout(yaxis_title="Faturamento (R$)")
                st.plotly_chart(fig_fat_ret, use_container_width=True)
                
                # Métricas de Faturamento Retornantes
                fat_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Líquido Total Consulta Plantão - Retornantes'].sum()
                fat_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Líquido Total Consulta Plantão - Retornantes'].sum()
                var_fat_ret = ((fat_ret_2024 - fat_ret_2023) / fat_ret_2023 * 100) if fat_ret_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Retornantes (2023 vs 2024)", 
                    f"{var_fat_ret:.1f}%",
                    delta=f"R$ {fat_ret_2024 - fat_ret_2023:,.2f}"
                )

            # Análise do Google
            st.subheader("Análise de Consultas Plantão via Google")
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de Clientes Google Novos
                fig_google_novos = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão - Google Novos',
                    color='Ano',
                    title=f'Evolução Consultas Google Plantão (Novos) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_google_novos, use_container_width=True)
                
                # Métricas Google Novos
                google_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão - Google Novos'].sum()
                google_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Google Novos'].sum()
                var_google_novos = ((google_novos_2024 - google_novos_2023) / google_novos_2023 * 100) if google_novos_2023 > 0 else 0
                st.metric(
                    "Variação Google Novos (2023 vs 2024)", 
                    f"{var_google_novos:.1f}%",
                    delta=f"{google_novos_2024 - google_novos_2023:.0f} consultas"
                )
            
            with col2:
                # Gráfico de Clientes Google Retornantes
                fig_google_ret = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão - Google Retornantes',
                    color='Ano',
                    title=f'Evolução Consultas Google Plantão (Retornantes) - {unidade_analise}',
                    markers=True
                )
                st.plotly_chart(fig_google_ret, use_container_width=True)
                
                # Métricas Google Retornantes
                google_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão - Google Retornantes'].sum()
                google_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão - Google Retornantes'].sum()
                var_google_ret = ((google_ret_2024 - google_ret_2023) / google_ret_2023 * 100) if google_ret_2023 > 0 else 0
                st.metric(
                    "Variação Google Retornantes (2023 vs 2024)", 
                    f"{var_google_ret:.1f}%",
                    delta=f"{google_ret_2024 - google_ret_2023:.0f} consultas"
                )

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            df_comp = df_unidade.pivot_table(
                values=['Total Consulta Plantão - Novos', 'Total Consulta Plantão - Retornantes',
                    'Faturamento Líquido Total Consulta Plantão - Novos', 
                    'Faturamento Líquido Total Consulta Plantão - Retornantes'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Calculando variações percentuais
            df_comp['Variação % Novos'] = ((df_comp[('Total Consulta Plantão - Novos', 2024)] - 
                                        df_comp[('Total Consulta Plantão - Novos', 2023)]) / 
                                        df_comp[('Total Consulta Plantão - Novos', 2023)] * 100).round(1)
            df_comp['Variação % Retornantes'] = ((df_comp[('Total Consulta Plantão - Retornantes', 2024)] - 
                                                df_comp[('Total Consulta Plantão - Retornantes', 2023)]) / 
                                                df_comp[('Total Consulta Plantão - Retornantes', 2023)] * 100).round(1)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela4A":
            st.subheader("Análise de Consultas Plantão por Dia")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Análise por tipo de plantão
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de evolução Domingo/Feriado
                fig_dom = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão Domingo/Feriado',
                    color='Ano',
                    title=f'Evolução Plantão Domingo/Feriado - {unidade_analise}',
                    markers=True
                )
                fig_dom.add_bar(
                    x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                    y=df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Domingo/Feriado'],
                    name='2024',
                    opacity=0.3
                )
                st.plotly_chart(fig_dom, use_container_width=True)
                
                # Métricas Domingo/Feriado
                total_dom_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão Domingo/Feriado'].sum()
                total_dom_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Domingo/Feriado'].sum()
                var_dom = ((total_dom_2024 - total_dom_2023) / total_dom_2023 * 100) if total_dom_2023 > 0 else 0
                st.metric(
                    "Variação Domingo/Feriado (2023 vs 2024)", 
                    f"{var_dom:.1f}%",
                    delta=f"{total_dom_2024 - total_dom_2023:.0f} consultas"
                )
            
            with col2:
                # Gráfico de evolução Noturno
                fig_not = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão Noturno',
                    color='Ano',
                    title=f'Evolução Plantão Noturno - {unidade_analise}',
                    markers=True
                )
                fig_not.add_bar(
                    x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                    y=df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Noturno'],
                    name='2024',
                    opacity=0.3
                )
                st.plotly_chart(fig_not, use_container_width=True)
                
                # Métricas Noturno
                total_not_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão Noturno'].sum()
                total_not_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Noturno'].sum()
                var_not = ((total_not_2024 - total_not_2023) / total_not_2023 * 100) if total_not_2023 > 0 else 0
                st.metric(
                    "Variação Noturno (2023 vs 2024)", 
                    f"{var_not:.1f}%",
                    delta=f"{total_not_2024 - total_not_2023:.0f} consultas"
                )

            # Gráfico de evolução Sábado
            st.subheader("Análise de Plantão Sábado")
            col1, col2 = st.columns(2)
            with col1:
                fig_sab = px.line(
                    df_unidade,
                    x='Mês',
                    y='Total Consulta Plantão Sábado',
                    color='Ano',
                    title=f'Evolução Plantão Sábado - {unidade_analise}',
                    markers=True
                )
                fig_sab.add_bar(
                    x=df_unidade[df_unidade['Ano'] == 2024]['Mês'],
                    y=df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Sábado'],
                    name='2024',
                    opacity=0.3
                )
                st.plotly_chart(fig_sab, use_container_width=True)
                
                # Métricas Sábado
                total_sab_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consulta Plantão Sábado'].sum()
                total_sab_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Sábado'].sum()
                var_sab = ((total_sab_2024 - total_sab_2023) / total_sab_2023 * 100) if total_sab_2023 > 0 else 0
                st.metric(
                    "Variação Sábado (2023 vs 2024)", 
                    f"{var_sab:.1f}%",
                    delta=f"{total_sab_2024 - total_sab_2023:.0f} consultas"
                )
            
            # Gráfico de distribuição percentual
            with col2:
                # Calcula o total de cada tipo para 2024
                total_dom = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Domingo/Feriado'].sum()
                total_not = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Noturno'].sum()
                total_sab = df_unidade[df_unidade['Ano'] == 2024]['Total Consulta Plantão Sábado'].sum()
                
                dados_pie = pd.DataFrame({
                    'Tipo': ['Domingo/Feriado', 'Noturno', 'Sábado'],
                    'Total': [total_dom, total_not, total_sab]
                })
                
                fig_dist = px.pie(
                    dados_pie,
                    values='Total',
                    names='Tipo',
                    title=f'Distribuição dos Tipos de Plantão em 2024 - {unidade_analise}'
                )
                st.plotly_chart(fig_dist, use_container_width=True)

            # Análise de Faturamento
            st.subheader("Análise de Faturamento por Tipo de Plantão")
            col1, col2 = st.columns(2)
            with col1:
                # Criando um DataFrame separado para melhor visualização
                df_fat_dn = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Domingo/Feriado': df_unidade['Faturamento Líquido Total Consulta Plantão Domingo/Feriado'],
                    'Noturno': df_unidade['Faturamento Líquido Total Consulta Plantão Noturno']
                })
                
                # Usando go.Figure para maior controle das cores
                fig_fat_dn = go.Figure()
                
                # Adicionando linha para Domingo/Feriado 2023
                fig_fat_dn.add_trace(go.Scatter(
                    x=df_fat_dn[df_fat_dn['Ano'] == 2023]['Mês'],
                    y=df_fat_dn[df_fat_dn['Ano'] == 2023]['Domingo/Feriado'],
                    name='Domingo/Feriado 2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Adicionando linha para Domingo/Feriado 2024
                fig_fat_dn.add_trace(go.Scatter(
                    x=df_fat_dn[df_fat_dn['Ano'] == 2024]['Mês'],
                    y=df_fat_dn[df_fat_dn['Ano'] == 2024]['Domingo/Feriado'],
                    name='Domingo/Feriado 2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Adicionando linha para Noturno 2023
                fig_fat_dn.add_trace(go.Scatter(
                    x=df_fat_dn[df_fat_dn['Ano'] == 2023]['Mês'],
                    y=df_fat_dn[df_fat_dn['Ano'] == 2023]['Noturno'],
                    name='Noturno 2023',
                    line=dict(color='#ff7f0e'),  # Laranja
                    mode='lines+markers'
                ))
                
                # Adicionando linha para Noturno 2024
                fig_fat_dn.add_trace(go.Scatter(
                    x=df_fat_dn[df_fat_dn['Ano'] == 2024]['Mês'],
                    y=df_fat_dn[df_fat_dn['Ano'] == 2024]['Noturno'],
                    name='Noturno 2024',
                    line=dict(color='#d62728'),  # Vermelho
                    mode='lines+markers'
                ))
                
                fig_fat_dn.update_layout(
                    title=f'Faturamento Domingo/Feriado e Noturno - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_dn, use_container_width=True)

        elif aba_selecionada in ["Tabela4B", "Tabela4C", "Tabela4D", "Tabela4E"]:
            tipos_plantao = {
                "Tabela4B": {
                    "nome": "Domingo/Feriado",
                    "padrao": True
                },
                "Tabela4C": {
                    "nome": "Sábado",
                    "padrao": True
                },
                "Tabela4D": {
                    "nome": "Emergencial",
                    "padrao": False,
                    "novos": "Total Consulta Procedimento Emergencial Plantão - Google Novos",
                    "retornantes": "Total Consulta Procedimento Emergencial Plantão - Google Retornantes",
                    "fat_novos": "Faturamento Líquido Total Consulta Procedimento Emergencial Plantão - Google Novos",
                    "fat_retornantes": "Faturamento Líquido Total Consulta Procedimento Emergencial Plantão - Google Retornantes"
                },
                "Tabela4E": {
                    "nome": "Noturno",
                    "padrao": False,
                    "novos": "Total Consulta Plantão Noturno Google Novos",
                    "retornantes": "Total Consulta Plantão Noturno Google Retornantes",
                    "fat_novos": "Faturamento Líquido Total Consulta Plantão Noturno Google Novos",
                    "fat_retornantes": "Faturamento Líquido Total Consulta Plantão Noturno Google Retornantes"
                }
            }
            
            tipo_atual = tipos_plantao[aba_selecionada]
            st.subheader(f"Análise de Consultas Plantão {tipo_atual['nome']}")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            col1, col2 = st.columns(2)
            with col1:
                # Consultas Google Novos
                df_google_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Google Novos': df_unidade[tipo_atual['novos'] if not tipo_atual['padrao'] else f'Total Consulta Plantão {tipo_atual["nome"]} - Google Novos']
                })
                
                fig_google_novos = go.Figure()
                
                # Linha para Google Novos 2023
                fig_google_novos.add_trace(go.Scatter(
                    x=df_google_novos[df_google_novos['Ano'] == 2023]['Mês'],
                    y=df_google_novos[df_google_novos['Ano'] == 2023]['Google Novos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para Google Novos 2024
                fig_google_novos.add_trace(go.Scatter(
                    x=df_google_novos[df_google_novos['Ano'] == 2024]['Mês'],
                    y=df_google_novos[df_google_novos['Ano'] == 2024]['Google Novos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_google_novos.update_layout(
                    title=f'Evolução Consultas {tipo_atual} via Google (Novos) - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_google_novos, use_container_width=True)
            
            with col2:
                # Consultas Google Retornantes
                df_google_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Google Retornantes': df_unidade[tipo_atual['retornantes'] if not tipo_atual['padrao'] else f'Total Consulta Plantão {tipo_atual["nome"]} - Google Retornantes']
                })
                
                fig_google_ret = go.Figure()
                
                # Linha para Google Retornantes 2023
                fig_google_ret.add_trace(go.Scatter(
                    x=df_google_ret[df_google_ret['Ano'] == 2023]['Mês'],
                    y=df_google_ret[df_google_ret['Ano'] == 2023]['Google Retornantes'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para Google Retornantes 2024
                fig_google_ret.add_trace(go.Scatter(
                    x=df_google_ret[df_google_ret['Ano'] == 2024]['Mês'],
                    y=df_google_ret[df_google_ret['Ano'] == 2024]['Google Retornantes'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_google_ret.update_layout(
                    title=f'Evolução Consultas {tipo_atual} via Google (Retornantes) - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_google_ret, use_container_width=True)

            # Nova linha para gráficos de faturamento
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Google Novos
                df_fat_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento Novos': df_unidade[tipo_atual['fat_novos'] if not tipo_atual['padrao'] else f'Faturamento Líquido Total Consulta Plantão {tipo_atual["nome"]} - Google Novos']
                })
                
                fig_fat_novos = go.Figure()
                
                # Linha para Faturamento Novos 2023
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2023]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2023]['Faturamento Novos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para Faturamento Novos 2024
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2024]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2024]['Faturamento Novos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_novos.update_layout(
                    title=f'Faturamento {tipo_atual} via Google (Novos) - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_novos, use_container_width=True)
                
                # Métricas Novos
                coluna_novos = tipo_atual['novos'] if not tipo_atual['padrao'] else f'Total Consulta Plantão {tipo_atual["nome"]} - Google Novos'
                total_novos_2023 = df_unidade[df_unidade['Ano'] == 2023][coluna_novos].sum()
                total_novos_2024 = df_unidade[df_unidade['Ano'] == 2024][coluna_novos].sum()
                var_novos = ((total_novos_2024 - total_novos_2023) / total_novos_2023 * 100) if total_novos_2023 > 0 else 0
                st.metric(
                    f"Variação Google Novos {tipo_atual} (2023 vs 2024)",
                    f"{var_novos:.1f}%",
                    delta=f"{total_novos_2024 - total_novos_2023:.0f} consultas"
                )
            
            with col2:
                # Faturamento Google Retornantes
                df_fat_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento Retornantes': df_unidade[tipo_atual['fat_retornantes'] if not tipo_atual['padrao'] else f'Faturamento Líquido Total Consulta Plantão {tipo_atual["nome"]} - Google Retornantes']
                })
                
                fig_fat_ret = go.Figure()
                
                # Linha para Faturamento Retornantes 2023
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2023]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2023]['Faturamento Retornantes'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para Faturamento Retornantes 2024
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2024]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2024]['Faturamento Retornantes'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_ret.update_layout(
                    title=f'Faturamento {tipo_atual} via Google (Retornantes) - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_ret, use_container_width=True)
                
                # Métricas Retornantes
                coluna_retornantes = tipo_atual['retornantes'] if not tipo_atual['padrao'] else f'Total Consulta Plantão {tipo_atual["nome"]} - Google Retornantes'
                total_ret_2023 = df_unidade[df_unidade['Ano'] == 2023][coluna_retornantes].sum()
                total_ret_2024 = df_unidade[df_unidade['Ano'] == 2024][coluna_retornantes].sum()
                var_ret = ((total_ret_2024 - total_ret_2023) / total_ret_2023 * 100) if total_ret_2023 > 0 else 0
                st.metric(
                    f"Variação Google Retornantes {tipo_atual} (2023 vs 2024)",
                    f"{var_ret:.1f}%",
                    delta=f"{total_ret_2024 - total_ret_2023:.0f} consultas"
                )

        elif aba_selecionada == "Tabela5":
            st.subheader("Faturamento por Categoria de Cliente")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Análise de Clientes
            col1, col2 = st.columns(2)
            with col1:
                # Evolução Clientes Novos
                df_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Clientes Novos': df_unidade['Total de Clientes Novos']
                })
                
                fig_novos = go.Figure()
                
                # Linha para 2023
                fig_novos.add_trace(go.Scatter(
                    x=df_novos[df_novos['Ano'] == 2023]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2023]['Clientes Novos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_novos.add_trace(go.Scatter(
                    x=df_novos[df_novos['Ano'] == 2024]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2024]['Clientes Novos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_novos.add_trace(go.Bar(
                    x=df_novos[df_novos['Ano'] == 2024]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2024]['Clientes Novos'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_novos.update_layout(
                    title=f'Evolução Clientes Novos - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_novos, use_container_width=True)
                
                # Métricas Novos
                total_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total de Clientes Novos'].sum()
                total_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total de Clientes Novos'].sum()
                var_novos = ((total_novos_2024 - total_novos_2023) / total_novos_2023 * 100) if total_novos_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Novos (2023 vs 2024)",
                    f"{var_novos:.1f}%",
                    delta=f"{total_novos_2024 - total_novos_2023:.0f} clientes"
                )
            
            with col2:
                # Evolução Clientes Retornantes
                df_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Clientes Retornantes': df_unidade['Total de Clientes Retornantes']
                })
                
                fig_ret = go.Figure()
                
                # Linha para 2023
                fig_ret.add_trace(go.Scatter(
                    x=df_ret[df_ret['Ano'] == 2023]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2023]['Clientes Retornantes'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_ret.add_trace(go.Scatter(
                    x=df_ret[df_ret['Ano'] == 2024]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2024]['Clientes Retornantes'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_ret.add_trace(go.Bar(
                    x=df_ret[df_ret['Ano'] == 2024]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2024]['Clientes Retornantes'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_ret.update_layout(
                    title=f'Evolução Clientes Retornantes - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_ret, use_container_width=True)
                
                # Métricas Retornantes
                total_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total de Clientes Retornantes'].sum()
                total_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total de Clientes Retornantes'].sum()
                var_ret = ((total_ret_2024 - total_ret_2023) / total_ret_2023 * 100) if total_ret_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Retornantes (2023 vs 2024)",
                    f"{var_ret:.1f}%",
                    delta=f"{total_ret_2024 - total_ret_2023:.0f} clientes"
                )

            # Análise de Faturamento
            st.subheader("Análise de Faturamento")
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Clientes Novos
                df_fat_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento': df_unidade['Faturamento Clientes Novos']
                })
                
                fig_fat_novos = go.Figure()
                
                # Linha para 2023
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2023]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2023]['Faturamento'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2024]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2024]['Faturamento'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_novos.update_layout(
                    title=f'Faturamento Clientes Novos - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_novos, use_container_width=True)
                
                # Métricas Faturamento Novos
                fat_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Clientes Novos'].sum()
                fat_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Clientes Novos'].sum()
                var_fat_novos = ((fat_novos_2024 - fat_novos_2023) / fat_novos_2023 * 100) if fat_novos_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Novos (2023 vs 2024)",
                    f"{var_fat_novos:.1f}%",
                    delta=f"R$ {fat_novos_2024 - fat_novos_2023:,.2f}"
                )
            
            with col2:
                # Faturamento Clientes Retornantes
                df_fat_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento': df_unidade['Faturamento Clientes Retornantes']
                })
                
                fig_fat_ret = go.Figure()
                
                # Linha para 2023
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2023]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2023]['Faturamento'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2024]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2024]['Faturamento'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_ret.update_layout(
                    title=f'Faturamento Clientes Retornantes - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_ret, use_container_width=True)
                
                # Métricas Faturamento Retornantes
                fat_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Clientes Retornantes'].sum()
                fat_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Clientes Retornantes'].sum()
                var_fat_ret = ((fat_ret_2024 - fat_ret_2023) / fat_ret_2023 * 100) if fat_ret_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Retornantes (2023 vs 2024)",
                    f"{var_fat_ret:.1f}%",
                    delta=f"R$ {fat_ret_2024 - fat_ret_2023:,.2f}"
                )

            # Métricas totais
            st.subheader("Métricas Consolidadas")
            col1, col2, col3 = st.columns(3)
            
            # Métricas para a unidade selecionada
            total_clientes_unidade = df_unidade['Total Clientes'].sum()
            faturamento_total_unidade = df_unidade['Faturamento Total'].sum()
            ticket_medio_unidade = faturamento_total_unidade / total_clientes_unidade if total_clientes_unidade > 0 else 0
            
            col1.metric("Total de Clientes", f"{total_clientes_unidade:,.0f}")
            col2.metric("Faturamento Total", f"R$ {faturamento_total_unidade:,.2f}")
            col3.metric("Ticket Médio", f"R$ {ticket_medio_unidade:,.2f}")

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            df_comp = df_unidade.pivot_table(
                values=['Total de Clientes Novos', 'Total de Clientes Retornantes',
                    'Faturamento Clientes Novos', 'Faturamento Clientes Retornantes'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Calculando variações percentuais
            for coluna in ['Total de Clientes Novos', 'Total de Clientes Retornantes']:
                df_comp[f'Variação % {coluna}'] = ((df_comp[(coluna, 2024)] - 
                                                df_comp[(coluna, 2023)]) / 
                                                df_comp[(coluna, 2023)] * 100).round(1)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela6":
            st.subheader("Faturamento Clientes Google")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Análise de Clientes Google
            col1, col2 = st.columns(2)
            with col1:
                # Evolução Clientes Google Novos
                df_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Clientes Google Novos': df_unidade['Total de Clientes Google Novos']
                })
                
                fig_novos = go.Figure()
                
                # Linha para 2023
                fig_novos.add_trace(go.Scatter(
                    x=df_novos[df_novos['Ano'] == 2023]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2023]['Clientes Google Novos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_novos.add_trace(go.Scatter(
                    x=df_novos[df_novos['Ano'] == 2024]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2024]['Clientes Google Novos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_novos.add_trace(go.Bar(
                    x=df_novos[df_novos['Ano'] == 2024]['Mês'],
                    y=df_novos[df_novos['Ano'] == 2024]['Clientes Google Novos'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_novos.update_layout(
                    title=f'Evolução Clientes Google Novos - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_novos, use_container_width=True)
                
                # Métricas Novos
                total_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total de Clientes Google Novos'].sum()
                total_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total de Clientes Google Novos'].sum()
                var_novos = ((total_novos_2024 - total_novos_2023) / total_novos_2023 * 100) if total_novos_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Google Novos (2023 vs 2024)",
                    f"{var_novos:.1f}%",
                    delta=f"{total_novos_2024 - total_novos_2023:.0f} clientes"
                )
            
            with col2:
                # Evolução Clientes Google Retornantes
                df_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Clientes Google Retornantes': df_unidade['Total de Clientes Google Retornantes']
                })
                
                fig_ret = go.Figure()
                
                # Linha para 2023
                fig_ret.add_trace(go.Scatter(
                    x=df_ret[df_ret['Ano'] == 2023]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2023]['Clientes Google Retornantes'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_ret.add_trace(go.Scatter(
                    x=df_ret[df_ret['Ano'] == 2024]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2024]['Clientes Google Retornantes'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_ret.add_trace(go.Bar(
                    x=df_ret[df_ret['Ano'] == 2024]['Mês'],
                    y=df_ret[df_ret['Ano'] == 2024]['Clientes Google Retornantes'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_ret.update_layout(
                    title=f'Evolução Clientes Google Retornantes - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_ret, use_container_width=True)
                
                # Métricas Retornantes
                total_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total de Clientes Google Retornantes'].sum()
                total_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total de Clientes Google Retornantes'].sum()
                var_ret = ((total_ret_2024 - total_ret_2023) / total_ret_2023 * 100) if total_ret_2023 > 0 else 0
                st.metric(
                    "Variação Clientes Google Retornantes (2023 vs 2024)",
                    f"{var_ret:.1f}%",
                    delta=f"{total_ret_2024 - total_ret_2023:.0f} clientes"
                )

            # Análise de Faturamento
            st.subheader("Análise de Faturamento Google")
            col1, col2 = st.columns(2)
            with col1:
                # Faturamento Google Novos
                df_fat_novos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento': df_unidade['Faturamento Google Novos']
                })
                
                fig_fat_novos = go.Figure()
                
                # Linha para 2023
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2023]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2023]['Faturamento'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_fat_novos.add_trace(go.Scatter(
                    x=df_fat_novos[df_fat_novos['Ano'] == 2024]['Mês'],
                    y=df_fat_novos[df_fat_novos['Ano'] == 2024]['Faturamento'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_novos.update_layout(
                    title=f'Faturamento Google Novos - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_novos, use_container_width=True)
                
                # Métricas Faturamento Novos
                fat_novos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Google Novos'].sum()
                fat_novos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Google Novos'].sum()
                var_fat_novos = ((fat_novos_2024 - fat_novos_2023) / fat_novos_2023 * 100) if fat_novos_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Google Novos (2023 vs 2024)",
                    f"{var_fat_novos:.1f}%",
                    delta=f"R$ {fat_novos_2024 - fat_novos_2023:,.2f}"
                )
            
            with col2:
                # Faturamento Google Retornantes
                df_fat_ret = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento': df_unidade['Faturamento Google Retornantes']
                })
                
                fig_fat_ret = go.Figure()
                
                # Linha para 2023
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2023]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2023]['Faturamento'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_fat_ret.add_trace(go.Scatter(
                    x=df_fat_ret[df_fat_ret['Ano'] == 2024]['Mês'],
                    y=df_fat_ret[df_fat_ret['Ano'] == 2024]['Faturamento'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_fat_ret.update_layout(
                    title=f'Faturamento Google Retornantes - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_fat_ret, use_container_width=True)
                
                # Métricas Faturamento Retornantes
                fat_ret_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Google Retornantes'].sum()
                fat_ret_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Google Retornantes'].sum()
                var_fat_ret = ((fat_ret_2024 - fat_ret_2023) / fat_ret_2023 * 100) if fat_ret_2023 > 0 else 0
                st.metric(
                    "Variação Faturamento Google Retornantes (2023 vs 2024)",
                    f"{var_fat_ret:.1f}%",
                    delta=f"R$ {fat_ret_2024 - fat_ret_2023:,.2f}"
                )

            # Métricas totais Google
            st.subheader("Métricas Consolidadas Google")
            col1, col2, col3 = st.columns(3)
            
            # Métricas para a unidade selecionada
            total_clientes_google = df_unidade['Total Clientes Google'].sum()
            faturamento_total_google = df_unidade['Faturamento Total Google'].sum()
            ticket_medio_google = faturamento_total_google / total_clientes_google if total_clientes_google > 0 else 0
            
            col1.metric("Total de Clientes Google", f"{total_clientes_google:,.0f}")
            col2.metric("Faturamento Total Google", f"R$ {faturamento_total_google:,.2f}")
            col3.metric("Ticket Médio Google", f"R$ {ticket_medio_google:,.2f}")

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            df_comp = df_unidade.pivot_table(
                values=['Total de Clientes Google Novos', 'Total de Clientes Google Retornantes',
                    'Faturamento Google Novos', 'Faturamento Google Retornantes'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Calculando variações percentuais
            for coluna in ['Total de Clientes Google Novos', 'Total de Clientes Google Retornantes']:
                df_comp[f'Variação % {coluna}'] = ((df_comp[(coluna, 2024)] - 
                                                df_comp[(coluna, 2023)]) / 
                                                df_comp[(coluna, 2023)] * 100).round(1)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela7":
            st.subheader("Ticket Médio Atendimento de Plantão")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Análise de Consultas
            col1, col2 = st.columns(2)
            with col1:
                # Evolução das Consultas
                df_consultas = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Total Consultas': df_unidade['Total Consultas Plantão']
                })
                
                fig_consultas = go.Figure()
                
                # Linha para 2023
                fig_consultas.add_trace(go.Scatter(
                    x=df_consultas[df_consultas['Ano'] == 2023]['Mês'],
                    y=df_consultas[df_consultas['Ano'] == 2023]['Total Consultas'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_consultas.add_trace(go.Scatter(
                    x=df_consultas[df_consultas['Ano'] == 2024]['Mês'],
                    y=df_consultas[df_consultas['Ano'] == 2024]['Total Consultas'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_consultas.add_trace(go.Bar(
                    x=df_consultas[df_consultas['Ano'] == 2024]['Mês'],
                    y=df_consultas[df_consultas['Ano'] == 2024]['Total Consultas'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_consultas.update_layout(
                    title=f'Evolução Consultas Plantão - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_consultas, use_container_width=True)
                
               # Métricas Consultas
                total_consultas_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total Consultas Plantão'].sum()
                total_consultas_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total Consultas Plantão'].sum()
                var_consultas = ((total_consultas_2024 - total_consultas_2023) / total_consultas_2023 * 100) if total_consultas_2023 > 0 else 0
                diferenca_consultas = total_consultas_2024 - total_consultas_2023

                st.metric(
                    "Variação Consultas (2023 vs 2024)",
                    f"{var_consultas:.1f}%",
                    delta=f"{diferenca_consultas:,.0f} consultas" if diferenca_consultas >= 0 else f"-{abs(diferenca_consultas):,.0f} consultas"
                )

               
                # Métricas Ticket Médio
                ticket_medio_2023 = df_unidade[df_unidade['Ano'] == 2023]['Ticket Médio de Atendimento de Plantão'].mean()
                ticket_medio_2024 = df_unidade[df_unidade['Ano'] == 2024]['Ticket Médio de Atendimento de Plantão'].mean()
                var_ticket = ((ticket_medio_2024 - ticket_medio_2023) / ticket_medio_2023 * 100) if ticket_medio_2023 > 0 else 0
                diferenca_ticket = ticket_medio_2024 - ticket_medio_2023

                st.metric(
                    "Variação Ticket Médio (2023 vs 2024)",
                    f"{var_ticket:.1f}%",
                    delta=f"R$ {diferenca_ticket:,.2f}" if diferenca_ticket >= 0 else f"-R$ {abs(diferenca_ticket):,.2f}"
                )

            # Análise de Faturamento
            st.subheader("Análise de Faturamento")
            col1, col2 = st.columns(2)
            with col1:
                # Evolução do Faturamento
                df_faturamento = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento': df_unidade['Faturamento Total Líquido de Serviços de Plantão']
                })
                
                fig_faturamento = go.Figure()
                
                # Linha para 2023
                fig_faturamento.add_trace(go.Scatter(
                    x=df_faturamento[df_faturamento['Ano'] == 2023]['Mês'],
                    y=df_faturamento[df_faturamento['Ano'] == 2023]['Faturamento'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_faturamento.add_trace(go.Scatter(
                    x=df_faturamento[df_faturamento['Ano'] == 2024]['Mês'],
                    y=df_faturamento[df_faturamento['Ano'] == 2024]['Faturamento'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_faturamento.update_layout(
                    title=f'Evolução Faturamento Plantão - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_faturamento, use_container_width=True)
                
                # Métricas Faturamento
                fat_total_2023 = df_unidade[df_unidade['Ano'] == 2023]['Faturamento Total Líquido de Serviços de Plantão'].sum()
                fat_total_2024 = df_unidade[df_unidade['Ano'] == 2024]['Faturamento Total Líquido de Serviços de Plantão'].sum()
                var_fat = ((fat_total_2024 - fat_total_2023) / fat_total_2023 * 100) if fat_total_2023 > 0 else 0
                diferenca_fat = fat_total_2024 - fat_total_2023

                st.metric(
                    "Variação Faturamento (2023 vs 2024)",
                    f"{var_fat:.1f}%",
                    delta=f"R$ {diferenca_fat:,.2f}" if diferenca_fat >= 0 else f"-R$ {abs(diferenca_fat):,.2f}"
                )
            
            with col2:
                # Gráfico de representatividade
                fig_rep = px.pie(
                    df_filtrado,
                    values='Faturamento Total Líquido de Serviços de Plantão',
                    names='Unidade',
                    title='Representatividade no Faturamento Total'
                )
                fig_rep.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_rep, use_container_width=True)

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            df_comp = df_unidade.pivot_table(
                values=['Total Consultas Plantão', 'Ticket Médio de Atendimento de Plantão',
                    'Faturamento Total Líquido de Serviços de Plantão'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Calculando variações percentuais
            for coluna in ['Total Consultas Plantão', 'Ticket Médio de Atendimento de Plantão']:
                df_comp[f'Variação % {coluna}'] = ((df_comp[(coluna, 2024)] - 
                                                df_comp[(coluna, 2023)]) / 
                                                df_comp[(coluna, 2023)] * 100).round(1)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela8":
            st.subheader("Ticket Médio de Planistas na Loja")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Gráficos comparativos para a unidade selecionada
            st.subheader(f"Análise Detalhada - {unidade_analise}")
            
            # Análise de Planos
            col1, col2 = st.columns(2)
            with col1:
                # Evolução do Total de Planos
                df_planos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Total Planos': df_unidade['Total de Planos']
                })
                
                fig_planos = go.Figure()
                
                # Linha para 2023
                fig_planos.add_trace(go.Scatter(
                    x=df_planos[df_planos['Ano'] == 2023]['Mês'],
                    y=df_planos[df_planos['Ano'] == 2023]['Total Planos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha e barras para 2024
                fig_planos.add_trace(go.Scatter(
                    x=df_planos[df_planos['Ano'] == 2024]['Mês'],
                    y=df_planos[df_planos['Ano'] == 2024]['Total Planos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                # Barras para 2024
                fig_planos.add_trace(go.Bar(
                    x=df_planos[df_planos['Ano'] == 2024]['Mês'],
                    y=df_planos[df_planos['Ano'] == 2024]['Total Planos'],
                    name='2024 (Barras)',
                    marker_color='rgba(44, 160, 44, 0.3)',  # Verde transparente
                    showlegend=False
                ))
                
                fig_planos.update_layout(
                    title=f'Evolução Total de Planos - {unidade_analise}',
                    yaxis_title="Quantidade",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_planos, use_container_width=True)
                
                # Métricas de Planos
                total_planos_2023 = df_unidade[df_unidade['Ano'] == 2023]['Total de Planos'].sum()
                total_planos_2024 = df_unidade[df_unidade['Ano'] == 2024]['Total de Planos'].sum()
                var_planos = ((total_planos_2024 - total_planos_2023) / total_planos_2023 * 100) if total_planos_2023 > 0 else 0
                diferenca_planos = total_planos_2024 - total_planos_2023
                
                st.metric(
                    "Variação Total de Planos (2023 vs 2024)",
                    f"{var_planos:.1f}%",
                    delta=f"{diferenca_planos:,.0f} planos" if diferenca_planos >= 0 else f"-{abs(diferenca_planos):,.0f} planos"
                )
            
            with col2:
                # Evolução do Ticket Médio de Produtos
                df_ticket_produtos = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Ticket Produtos': df_unidade['Ticket Médio de Produtos do Planista']
                })
                
                fig_ticket_produtos = go.Figure()
                
                # Linha para 2023
                fig_ticket_produtos.add_trace(go.Scatter(
                    x=df_ticket_produtos[df_ticket_produtos['Ano'] == 2023]['Mês'],
                    y=df_ticket_produtos[df_ticket_produtos['Ano'] == 2023]['Ticket Produtos'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_ticket_produtos.add_trace(go.Scatter(
                    x=df_ticket_produtos[df_ticket_produtos['Ano'] == 2024]['Mês'],
                    y=df_ticket_produtos[df_ticket_produtos['Ano'] == 2024]['Ticket Produtos'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_ticket_produtos.update_layout(
                    title=f'Evolução Ticket Médio Produtos - {unidade_analise}',
                    yaxis_title="Valor (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_ticket_produtos, use_container_width=True)
                
                # Métricas de Ticket Produtos
                ticket_prod_2023 = df_unidade[df_unidade['Ano'] == 2023]['Ticket Médio de Produtos do Planista'].mean()
                ticket_prod_2024 = df_unidade[df_unidade['Ano'] == 2024]['Ticket Médio de Produtos do Planista'].mean()
                var_ticket_prod = ((ticket_prod_2024 - ticket_prod_2023) / ticket_prod_2023 * 100) if ticket_prod_2023 > 0 else 0
                diferenca_ticket_prod = ticket_prod_2024 - ticket_prod_2023
                
                st.metric(
                    "Variação Ticket Médio Produtos (2023 vs 2024)",
                    f"{var_ticket_prod:.1f}%",
                    delta=f"R$ {diferenca_ticket_prod:,.2f}" if diferenca_ticket_prod >= 0 else f"-R$ {abs(diferenca_ticket_prod):,.2f}"
                )

            # Análise do Ticket Médio Total
            st.subheader("Análise do Ticket Médio Total")
            col1, col2 = st.columns(2)
            with col1:
                # Evolução do Ticket Médio Total
                df_ticket_total = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Ticket Total': df_unidade['Ticket Médio Total do Planista']
                })
                
                fig_ticket_total = go.Figure()
                
                # Linha para 2023
                fig_ticket_total.add_trace(go.Scatter(
                    x=df_ticket_total[df_ticket_total['Ano'] == 2023]['Mês'],
                    y=df_ticket_total[df_ticket_total['Ano'] == 2023]['Ticket Total'],
                    name='2023',
                    line=dict(color='#1f77b4'),  # Azul
                    mode='lines+markers'
                ))
                
                # Linha para 2024
                fig_ticket_total.add_trace(go.Scatter(
                    x=df_ticket_total[df_ticket_total['Ano'] == 2024]['Mês'],
                    y=df_ticket_total[df_ticket_total['Ano'] == 2024]['Ticket Total'],
                    name='2024',
                    line=dict(color='#2ca02c'),  # Verde
                    mode='lines+markers'
                ))
                
                fig_ticket_total.update_layout(
                    title=f'Evolução Ticket Médio Total - {unidade_analise}',
                    yaxis_title="Valor (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_ticket_total, use_container_width=True)
                
                # Métricas de Ticket Total
                ticket_total_2023 = df_unidade[df_unidade['Ano'] == 2023]['Ticket Médio Total do Planista'].mean()
                ticket_total_2024 = df_unidade[df_unidade['Ano'] == 2024]['Ticket Médio Total do Planista'].mean()
                var_ticket_total = ((ticket_total_2024 - ticket_total_2023) / ticket_total_2023 * 100) if ticket_total_2023 > 0 else 0
                diferenca_ticket_total = ticket_total_2024 - ticket_total_2023
                
                st.metric(
                    "Variação Ticket Médio Total (2023 vs 2024)",
                    f"{var_ticket_total:.1f}%",
                    delta=f"R$ {diferenca_ticket_total:,.2f}" if diferenca_ticket_total >= 0 else f"-R$ {abs(diferenca_ticket_total):,.2f}"
                )
            
            with col2:
                # Gráfico de representatividade
                fig_rep = px.pie(
                    df_filtrado,
                    values='Representatividade no Faturamento Total da Loja (%)',
                    names='Unidade',
                    title='Representatividade no Faturamento Total da Loja'
                )
                fig_rep.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_rep, use_container_width=True)

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            df_comp = df_unidade.pivot_table(
                values=['Total de Planos', 'Ticket Médio de Produtos do Planista',
                    'Ticket Médio Total do Planista'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Calculando variações percentuais
            for coluna in ['Total de Planos', 'Ticket Médio de Produtos do Planista',
                        'Ticket Médio Total do Planista']:
                df_comp[f'Variação % {coluna}'] = ((df_comp[(coluna, 2024)] - 
                                                df_comp[(coluna, 2023)]) / 
                                                df_comp[(coluna, 2023)] * 100).round(1)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela9":
            st.subheader("Análise de Impacto dos Planistas no Hospital")
            st.write("Esta análise visa entender quanto os clientes com plano de banho e tosa contribuem para o faturamento do hospital, ajudando a avaliar se a estratégia de planos mais acessíveis resulta em maior faturamento hospitalar.")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            
            # Filtra dados da unidade selecionada
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Métricas Principais
            st.subheader("Métricas Principais")
            col1, col2, col3 = st.columns(3)
            
            # Cálculo da Taxa de Conversão (quanto do faturamento do hospital vem dos planistas)
            fat_total_hospital = df_unidade['Faturamento Total Líquido Hospital'].sum()
            fat_total_planistas = df_unidade['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'].sum()
            taxa_conversao = (fat_total_planistas / fat_total_hospital * 100) if fat_total_hospital > 0 else 0
            
            col1.metric(
                "Taxa de Conversão Planista → Hospital",
                f"{taxa_conversao:.1f}%",
                help="Percentual do faturamento do hospital que vem de clientes planistas"
            )
            
            # Ticket Médio comparativo
            ticket_medio_planista = df_unidade['Ticket Médio do Planista no Hospital'].mean()
            col2.metric(
                "Ticket Médio Planista no Hospital",
                f"R$ {ticket_medio_planista:,.2f}",
                help="Valor médio gasto por planista em serviços hospitalares"
            )
            
            # Representatividade
            representatividade = df_unidade['Representatividade no Faturamento Total do Hospital (%)'].mean()
            col3.metric(
                "Representatividade no Hospital",
                f"{representatividade:.1f}%",
                help="Quanto os planistas representam no faturamento total do hospital"
            )

            # Análise de Tendências
            st.subheader("Análise de Tendências")
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico combinado de faturamento
                df_tendencia = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Fat. Hospital': df_unidade['Faturamento Total Líquido Hospital'],
                    'Fat. Planistas': df_unidade['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'],
                    'Representatividade (%)': df_unidade['Representatividade no Faturamento Total do Hospital (%)']
                })
                
                fig_tendencia = go.Figure()
                
                # Faturamento Hospital 2023
                fig_tendencia.add_trace(go.Bar(
                    x=df_tendencia[df_tendencia['Ano'] == 2023]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2023]['Fat. Hospital'],
                    name='Hospital 2023',
                    marker_color='rgba(27, 119, 180, 0.4)'
                ))
                
                # Faturamento Hospital 2024
                fig_tendencia.add_trace(go.Bar(
                    x=df_tendencia[df_tendencia['Ano'] == 2024]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2024]['Fat. Hospital'],
                    name='Hospital 2024',
                    marker_color='rgba(44, 160, 44, 0.4)'
                ))
                
                # Faturamento Planistas como linha
                fig_tendencia.add_trace(go.Scatter(
                    x=df_tendencia[df_tendencia['Ano'] == 2023]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2023]['Fat. Planistas'],
                    name='Planistas 2023',
                    line=dict(color='#1f77b4', width=2),
                    mode='lines+markers'
                ))
                
                fig_tendencia.add_trace(go.Scatter(
                    x=df_tendencia[df_tendencia['Ano'] == 2024]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2024]['Fat. Planistas'],
                    name='Planistas 2024',
                    line=dict(color='#2ca02c', width=2),
                    mode='lines+markers'
                ))
                
                fig_tendencia.update_layout(
                    title=f'Relação entre Faturamento Hospital e Planistas - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    barmode='group',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_tendencia, use_container_width=True)
            
            with col2:
                # Evolução da representatividade
                fig_rep = go.Figure()
                
                fig_rep.add_trace(go.Scatter(
                    x=df_tendencia[df_tendencia['Ano'] == 2023]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2023]['Representatividade (%)'],
                    name='2023',
                    line=dict(color='#1f77b4'),
                    mode='lines+markers'
                ))
                
                fig_rep.add_trace(go.Scatter(
                    x=df_tendencia[df_tendencia['Ano'] == 2024]['Mês'],
                    y=df_tendencia[df_tendencia['Ano'] == 2024]['Representatividade (%)'],
                    name='2024',
                    line=dict(color='#2ca02c'),
                    mode='lines+markers'
                ))
                
                fig_rep.update_layout(
                    title=f'Evolução da Representatividade dos Planistas - {unidade_analise}',
                    yaxis_title="Representatividade (%)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_rep, use_container_width=True)

            # Análise de Correlação
            st.subheader("Análise de Correlação")
            col1, col2 = st.columns(2)
            
            with col1:
                # Criando DataFrame para o gráfico
                df_barras = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Faturamento Planistas': df_unidade['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'],
                    'Faturamento Outros': df_unidade['Faturamento Total Líquido Hospital'] - df_unidade['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital']
                })

                fig_barras = go.Figure()

                # Adicionando barras para cada ano
                for ano in sorted(df_barras['Ano'].unique()):
                    df_ano = df_barras[df_barras['Ano'] == ano]
                    
                    # Barra de Faturamento Planistas
                    fig_barras.add_trace(go.Bar(
                        name=f'Planistas {ano}',
                        x=df_ano['Mês'],
                        y=df_ano['Faturamento Planistas'],
                        marker_color='#1f77b4' if ano == 2023 else '#2ca02c'
                    ))
                    
                    # Barra de Outros Faturamentos
                    fig_barras.add_trace(go.Bar(
                        name=f'Outros {ano}',
                        x=df_ano['Mês'],
                        y=df_ano['Faturamento Outros'],
                        marker_color='rgba(27, 119, 180, 0.3)' if ano == 2023 else 'rgba(44, 160, 44, 0.3)'
                    ))

                fig_barras.update_layout(
                    title=f'Composição do Faturamento Hospital - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    barmode='stack',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    hovermode='x'
                )
                
                # Formatando o eixo Y para mostrar valores em R$
                fig_barras.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
                
                # Adicionando hover template mais informativo
                for trace in fig_barras.data:
                    trace.hovertemplate = "%{x}<br>" + \
                                        "%{data.name}: R$ %{y:,.2f}<br>" + \
                                        "<extra></extra>"
                
                st.plotly_chart(fig_barras, use_container_width=True)
            
            with col2:
                # Gráfico de representatividade por unidade
                fig_rep_unidade = px.pie(
                    df_filtrado,
                    values='Representatividade no Faturamento Total do Hospital (%)',
                    names='Unidade',
                    title='Comparativo de Representatividade entre Unidades'
                )
                fig_rep_unidade.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_rep_unidade, use_container_width=True)

            # Resumo e Insights
            st.subheader("Insights")
            col1, col2 = st.columns(2)
            
            # Variações ano a ano
            with col1:
                var_fat_hosp = ((df_unidade[df_unidade['Ano'] == 2024]['Faturamento Total Líquido Hospital'].sum() - 
                                df_unidade[df_unidade['Ano'] == 2023]['Faturamento Total Líquido Hospital'].sum()) / 
                                df_unidade[df_unidade['Ano'] == 2023]['Faturamento Total Líquido Hospital'].sum() * 100)
                
                var_fat_plan = ((df_unidade[df_unidade['Ano'] == 2024]['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'].sum() - 
                                df_unidade[df_unidade['Ano'] == 2023]['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'].sum()) / 
                                df_unidade[df_unidade['Ano'] == 2023]['Faturamento Total Líquido do Consumo do Planista em serviço no Hospital'].sum() * 100)
                
                st.metric("Variação Faturamento Hospital (2023 vs 2024)", f"{var_fat_hosp:.1f}%")
                st.metric("Variação Faturamento Planistas (2023 vs 2024)", f"{var_fat_plan:.1f}%")
            
            with col2:
                var_rep = ((df_unidade[df_unidade['Ano'] == 2024]['Representatividade no Faturamento Total do Hospital (%)'].mean() - 
                            df_unidade[df_unidade['Ano'] == 2023]['Representatividade no Faturamento Total do Hospital (%)'].mean()))
                
                st.metric("Variação na Representatividade (2023 vs 2024)", 
                        f"{var_rep:.1f} p.p.",
                        help="Variação em pontos percentuais da representatividade dos planistas no faturamento do hospital")

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")

            # Criar ordem padrão para os meses
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

            # Converter mês para categoria ordenada
            df_unidade['Mês'] = pd.Categorical(df_unidade['Mês'], categories=ordem_meses, ordered=True)

            # Criar pivot table com meses ordenados
            df_comp = df_unidade.pivot_table(
                values=['Faturamento Total Líquido Hospital',
                        'Faturamento Total Líquido do Consumo do Planista em serviço no Hospital',
                        'Representatividade no Faturamento Total do Hospital (%)'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)

            # Reordenar o índice conforme a ordem dos meses
            df_comp = df_comp.reindex(ordem_meses)

            # Calculando variações percentuais
            for coluna in df_comp.index.get_level_values(0).unique():
                try:
                    valor_2023 = df_comp.loc[coluna, (coluna, 2023)]
                    valor_2024 = df_comp.loc[coluna, (coluna, 2024)]
                    if pd.notnull(valor_2023) and valor_2023 != 0:
                        variacao = ((valor_2024 - valor_2023) / valor_2023 * 100).round(1)
                    else:
                        variacao = 0
                    df_comp.loc[coluna, f'Variação % {coluna}'] = variacao
                except:
                    continue

            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela10":
            st.subheader("Análise de Impacto dos Planistas no Faturamento Global")
            st.write("""Esta análise visa entender o quanto os clientes de banho e tosa (planistas) impactam no faturamento do hospital. 
                    O objetivo é avaliar se a estratégia de manter planos de banho e tosa, mesmo com valores reduzidos, 
                    se justifica pelo consumo destes clientes dentro do hospital.""")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Métricas Principais
            st.subheader("Métricas Principais")
            col1, col2, col3, col4 = st.columns(4)
            
            # Faturamento Total do Hospital
            fat_hospital = df_unidade['Faturamento Total Hospital'].sum()
            col1.metric(
                "Faturamento Hospital",
                f"R$ {fat_hospital:,.2f}",
                help="Faturamento total do hospital no período"
            )
            
            # Faturamento dos Planistas sem considerar o plano
            fat_planista_sem = df_unidade['Faturamento Total Líquido do Consumo do Planista (sem o plano)'].sum()
            col2.metric(
                "Consumo Planistas no Hospital",
                f"R$ {fat_planista_sem:,.2f}",
                help="Quanto os planistas consumiram em serviços hospitalares (sem contar o valor do plano)"
            )
            
            # Faturamento dos Planistas incluindo o plano
            fat_planista_com = df_unidade['Faturamento Total Líquido do Consumo do Planista (com o plano)'].sum()
            col3.metric(
                "Consumo Total Planistas",
                f"R$ {fat_planista_com:,.2f}",
                help="Consumo total dos planistas incluindo o valor do plano"
            )
            
            # Representatividade
            representatividade = df_unidade['Representatividade do Planista (com o plano) no Faturamento Global (%)'].mean()
            col4.metric(
                "Representatividade Global",
                f"{representatividade:.1f}%",
                help="Percentual que os planistas representam no faturamento global"
            )

            # Análise de Composição do Faturamento
            st.subheader("Composição do Faturamento")
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras empilhadas mostrando a composição mensal
                df_comp = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Banho e Tosa': df_unidade['Faturamento Total Banho e Tosa'],
                    'Loja': df_unidade['Faturamento Total Loja'] - df_unidade['Faturamento Total Banho e Tosa'],
                    'Hospital': df_unidade['Faturamento Total Hospital']
                })
                
                fig_comp = go.Figure()
                
                for ano in df_comp['Ano'].unique():
                    df_ano = df_comp[df_comp['Ano'] == ano]
                    
                    # Adiciona barras empilhadas para cada componente
                    fig_comp.add_trace(go.Bar(
                        name=f'Hospital {ano}',
                        x=df_ano['Mês'],
                        y=df_ano['Hospital'],
                        marker_color='#1f77b4' if ano == 2023 else '#2ca02c'
                    ))
                    
                    fig_comp.add_trace(go.Bar(
                        name=f'Loja {ano}',
                        x=df_ano['Mês'],
                        y=df_ano['Loja'],
                        marker_color='rgba(27, 119, 180, 0.7)' if ano == 2023 else 'rgba(44, 160, 44, 0.7)'
                    ))
                    
                    fig_comp.add_trace(go.Bar(
                        name=f'Banho e Tosa {ano}',
                        x=df_ano['Mês'],
                        y=df_ano['Banho e Tosa'],
                        marker_color='rgba(27, 119, 180, 0.4)' if ano == 2023 else 'rgba(44, 160, 44, 0.4)'
                    ))
                
                fig_comp.update_layout(
                    barmode='stack',
                    title=f'Composição do Faturamento por Área - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
            
            with col2:
               # Gráfico comparativo do consumo dos planistas no hospital
                df_planista = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Consumo Total (com plano)': df_unidade['Faturamento Total Líquido do Consumo do Planista (com o plano)'],
                    'Consumo (sem plano)': df_unidade['Faturamento Total Líquido do Consumo do Planista (sem o plano)']
                })

                fig_planista = go.Figure()

                for ano in df_planista['Ano'].unique():
                    df_ano = df_planista[df_planista['Ano'] == ano]
                    
                    # Linha para consumo com plano
                    fig_planista.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Consumo Total (com plano)'],
                        name=f'Com Plano {ano}',
                        mode='lines+markers',
                        line=dict(color='#1f77b4' if ano == 2023 else '#2ca02c', width=2)
                    ))
                    
                    # Linha para consumo sem plano
                    fig_planista.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Consumo (sem plano)'],
                        name=f'Sem Plano {ano}',
                        mode='lines+markers',
                        line=dict(color='rgba(27, 119, 180, 0.5)' if ano == 2023 else 'rgba(44, 160, 44, 0.5)', width=2)
                    ))

                fig_planista.update_layout(
                    title=f'Consumo dos Planistas no Hospital - {unidade_analise}',
                    yaxis_title="Faturamento (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig_planista, use_container_width=True)

            # Análise de Retorno sobre Plano
            st.subheader("Análise de Retorno sobre Plano")
            col1, col2 = st.columns(2)
            
            with col1:
                # Cálculo do retorno sobre o valor do plano
                df_retorno = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Retorno': df_unidade['Faturamento Total Líquido do Consumo do Planista (sem o plano)'] / 
                            (df_unidade['Faturamento Total Líquido do Consumo do Planista (com o plano)'] - 
                            df_unidade['Faturamento Total Líquido do Consumo do Planista (sem o plano)'])
                })
                
                fig_retorno = go.Figure()
                
                for ano in df_retorno['Ano'].unique():
                    df_ano = df_retorno[df_retorno['Ano'] == ano]
                    
                    fig_retorno.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Retorno'],
                        name=str(ano),
                        mode='lines+markers',
                        line=dict(color='#1f77b4' if ano == 2023 else '#2ca02c')
                    ))
                
                fig_retorno.update_layout(
                    title=f'Retorno sobre Valor do Plano - {unidade_analise}',
                    yaxis_title="Retorno (R$ consumido / R$ plano)",
                    xaxis_title="Mês"
                )
                
                st.plotly_chart(fig_retorno, use_container_width=True)
            
            with col2:
                # Gráfico de pizza da representatividade por unidade
                fig_rep = px.pie(
                    df_filtrado,
                    values='Representatividade do Planista (com o plano) no Faturamento Global (%)',
                    names='Unidade',
                    title='Representatividade dos Planistas por Unidade'
                )
                fig_rep.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_rep, use_container_width=True)

            # Tabela de comparativo mensal detalhado
            st.subheader("Comparativo Mensal Detalhado")
            
            # Criando o comparativo mensal
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            df_unidade['Mês'] = pd.Categorical(df_unidade['Mês'], categories=ordem_meses, ordered=True)
            
            df_comp = df_unidade.pivot_table(
                values=['Faturamento Total Banho e Tosa',
                        'Faturamento Total Hospital',
                        'Faturamento Total Líquido do Consumo do Planista (sem o plano)',
                        'Faturamento Total Líquido do Consumo do Planista (com o plano)',
                        'Representatividade do Planista (com o plano) no Faturamento Global (%)'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            # Reordenando os meses
            df_comp = df_comp.reindex(ordem_meses)
            
            st.dataframe(df_comp)

        elif aba_selecionada == "Tabela11":
            st.subheader("Análise de Conversão de Receitas Médicas em Farmácia")
            st.write("""Esta análise acompanha a jornada dos clientes após consultas e altas, avaliando a conversão das receitas médicas em 
                    compras em nossa farmácia, incluindo o comportamento de compra ao longo do tempo.""")
            
            # Seletor de unidade para análise detalhada
            unidade_analise = st.selectbox("Selecione a unidade para análise detalhada:", unidades)
            df_unidade = df_filtrado[df_filtrado['Unidade'] == unidade_analise]
            
            # Métricas Principais
            st.subheader("Métricas Principais")
            col1, col2, col3, col4 = st.columns(4)
            
            # Total de consultas e conversão geral
            total_consultas = df_unidade['Número de consultas'].sum()
            total_farmacia = df_unidade['Número total de clientes únicos em farmácia pós consulta'].sum()
            
            col1.metric(
                "Total de Consultas",
                f"{total_consultas:,.0f}",
                help="Número total de consultas realizadas"
            )
            
            col2.metric(
                "Conversão Geral em Farmácia",
                f"{df_unidade['% Conversão de receitas pós consulta em Farmácia'].mean():.1f}%",
                help="Percentual médio de conversão de receitas em vendas na farmácia"
            )
            
            col3.metric(
                "Conversão no Mesmo Dia",
                f"{(df_unidade['Número de clientes em farmácia no mesmo dia da consulta'].sum() / total_consultas * 100):.1f}%",
                help="Percentual de clientes que compraram na farmácia no mesmo dia da consulta"
            )
            
            col4.metric(
                "Conversão de Alta",
                f"{df_unidade['% Conversão de receitas alta em Farmácia'].mean():.1f}%",
                help="Percentual de conversão de receitas de alta em vendas na farmácia"
            )

            # Análise Temporal da Conversão
            st.subheader("Evolução da Conversão")
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de linha temporal da conversão
                df_conversao = pd.DataFrame({
                    'Mês': df_unidade['Mês'],
                    'Ano': df_unidade['Ano'],
                    'Conversão Consulta (%)': df_unidade['% Conversão de receitas pós consulta em Farmácia'],
                    'Conversão Alta (%)': df_unidade['% Conversão de receitas alta em Farmácia']
                })
                
                fig_conversao = go.Figure()
                
                for ano in df_conversao['Ano'].unique():
                    df_ano = df_conversao[df_conversao['Ano'] == ano]
                    
                    # Linha para conversão de consultas
                    fig_conversao.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Conversão Consulta (%)'],
                        name=f'Consulta {ano}',
                        mode='lines+markers',
                        line=dict(color='#1f77b4' if ano == 2023 else '#2ca02c')
                    ))
                    
                    # Linha para conversão de altas
                    fig_conversao.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Conversão Alta (%)'],
                        name=f'Alta {ano}',
                        mode='lines+markers',
                        line=dict(dash='dash', color='#1f77b4' if ano == 2023 else '#2ca02c')
                    ))
                
                fig_conversao.update_layout(
                    title=f'Evolução da Taxa de Conversão - {unidade_analise}',
                    yaxis_title="Taxa de Conversão (%)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_conversao, use_container_width=True)
            
            with col2:
                # Gráfico de valor médio por cliente
                df_valor = df_unidade.copy()
                df_valor['Valor Médio por Cliente'] = df_valor['Valor líquido em venda, de clientes pós consulta, em farmácia durante todo o mês analisado'] / \
                                                    df_valor['Número total de clientes únicos em farmácia pós consulta']
                
                fig_valor = go.Figure()
                
                for ano in df_valor['Ano'].unique():
                    df_ano = df_valor[df_valor['Ano'] == ano]
                    
                    fig_valor.add_trace(go.Scatter(
                        x=df_ano['Mês'],
                        y=df_ano['Valor Médio por Cliente'],
                        name=str(ano),
                        mode='lines+markers',
                        line=dict(color='#1f77b4' if ano == 2023 else '#2ca02c')
                    ))
                
                fig_valor.update_layout(
                    title=f'Valor Médio por Cliente - {unidade_analise}',
                    yaxis_title="Valor Médio (R$)",
                    xaxis_title="Mês",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_valor, use_container_width=True)

            # Análise da Jornada de Conversão
            st.subheader("Jornada de Conversão")
            col1, col2 = st.columns(2)
            
            with col1:
                # Funil de conversão por tempo
                total_consultas = df_unidade['Número de consultas'].sum()
                mesmo_dia = df_unidade['Número de clientes em farmácia no mesmo dia da consulta'].sum()
                dia_seguinte = df_unidade['Número de clientes em farmácia no dia seguinte da consulta'].sum()
                dias_3_7 = df_unidade['Número de clientes em farmácia de 3 a 7 dias após a consulta'].sum()
                dias_8_mais = df_unidade['Número de clientes em farmácia 8 dias após a consulta'].sum()

                fig_funil = go.Figure(go.Funnel(
                    name='Funil de Conversão',
                    y=['Total Consultas', 'Mesmo Dia', 'Dia Seguinte', '3-7 dias', '8+ dias'],
                    x=[total_consultas, mesmo_dia, dia_seguinte, dias_3_7, dias_8_mais],
                    textinfo="value+percent initial"
                ))

                fig_funil.update_layout(
                    title=f'Funil de Conversão Temporal - {unidade_analise}',
                    showlegend=False
                )
                
                st.plotly_chart(fig_funil, use_container_width=True)
            
            with col2:
                # Gráfico de valor por momento de compra
                valores_momento = pd.DataFrame({
                    'Momento': ['Mesmo Dia', '3-7 dias', '8+ dias'],
                    'Valor': [
                        df_unidade['Valor líquido em venda de clientes em farmácia no mesmo dia da consulta'].sum(),
                        # Aqui precisaríamos dos valores para 3-7 dias e 8+ dias se disponíveis
                        0,  # placeholder
                        0   # placeholder
                    ]
                })
                
                fig_valor_momento = px.bar(
                    valores_momento,
                    x='Momento',
                    y='Valor',
                    title=f'Valor de Venda por Momento de Compra - {unidade_analise}'
                )
                
                st.plotly_chart(fig_valor_momento, use_container_width=True)

            # Análise Comparativa entre Unidades
            st.subheader("Comparativo entre Unidades")
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras de conversão por unidade
                fig_unidades = px.bar(
                    df_filtrado.groupby('Unidade').agg({
                        '% Conversão de receitas pós consulta em Farmácia': 'mean',
                        '% Conversão de receitas alta em Farmácia': 'mean'
                    }).reset_index(),
                    x='Unidade',
                    y=['% Conversão de receitas pós consulta em Farmácia', '% Conversão de receitas alta em Farmácia'],
                    title='Taxa de Conversão por Unidade',
                    barmode='group'
                )
                
                st.plotly_chart(fig_unidades, use_container_width=True)
            
            with col2:
                # Gráfico de valor médio por unidade
                fig_valor_unidade = px.bar(
                    df_filtrado.groupby('Unidade').agg({
                        'Valor líquido em venda, de clientes pós consulta, em farmácia durante todo o mês analisado': 'mean'
                    }).reset_index(),
                    x='Unidade',
                    y='Valor líquido em venda, de clientes pós consulta, em farmácia durante todo o mês analisado',
                    title='Valor Médio Mensal por Unidade'
                )
                
                st.plotly_chart(fig_valor_unidade, use_container_width=True)

            # Tabela de comparativo mensal
            st.subheader("Comparativo Mensal Detalhado")
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            df_unidade['Mês'] = pd.Categorical(df_unidade['Mês'], categories=ordem_meses, ordered=True)
            
            df_comp = df_unidade.pivot_table(
                values=['Número de consultas',
                        'Número total de clientes únicos em farmácia pós consulta',
                        '% Conversão de receitas pós consulta em Farmácia',
                        'Valor líquido em venda, de clientes pós consulta, em farmácia durante todo o mês analisado',
                        '% Conversão de receitas alta em Farmácia'],
                index='Mês',
                columns='Ano',
                aggfunc='sum'
            ).round(2)
            
            df_comp = df_comp.reindex(ordem_meses)
            
            st.dataframe(df_comp)

    except Exception as e:
        st.error(f'Erro ao carregar o arquivo: {str(e)}')

if __name__ == '__main__':
    criar_dashboard()