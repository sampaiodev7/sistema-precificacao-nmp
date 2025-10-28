"""
Sistema de Precificação Estratégica
Aplicação Principal
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Importar módulos personalizados
from modules.sheets import SheetsManager
from modules.auth import GerenciadorAutenticacao
from modules.calculos import CalculadoraMarkup
from modules.graficos import GeradorGraficos

# Configuração da página
st.set_page_config(
    page_title="Sistema de Precificação",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #9333ea 0%, #7c3aed 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #9333ea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #9333ea;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sessão
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['authenticated'] = False

def inicializar_conexao():
    """Inicializa conexão com Google Sheets"""
    try:
        # Tentar carregar credenciais do st.secrets (Streamlit Cloud)
        if 'gcp_service_account' in st.secrets:
            credentials_info = dict(st.secrets['gcp_service_account'])
            spreadsheet_id = st.secrets.get('SPREADSHEET_ID', '')
        # Senão, tentar carregar de arquivo local
        elif os.path.exists('service_account.json'):
            with open('service_account.json', 'r') as f:
                credentials_info = json.load(f)
            spreadsheet_id = os.getenv('SPREADSHEET_ID', '')
        else:
            st.error("""
            ❌ Credenciais não encontradas!
            
            Configure as credenciais de uma das formas:
            1. Streamlit Cloud: Adicione em Secrets
            2. Local: Crie arquivo service_account.json
            """)
            st.stop()
        
        if not spreadsheet_id:
            st.error("SPREADSHEET_ID não configurado!")
            st.stop()
        
        sheets_manager = SheetsManager(spreadsheet_id, credentials_info)
        return sheets_manager
        
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        st.stop()

def exibir_header():
    """Exibe cabeçalho da aplicação"""
    st.markdown("""
    <div class="main-header">
        <h1>💰 Sistema de Precificação Estratégica</h1>
        <p>Gerencie custos, calcule preços e maximize sua rentabilidade</p>
    </div>
    """, unsafe_allow_html=True)

def exibir_info_usuario():
    """Exibe informações do usuário logado"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"**Olá, {st.session_state.get('display_name', 'Usuário')}!** 👋")
    
    with col2:
        role = st.session_state.get('role', 'user')
        if role == 'admin':
            st.markdown("🔑 **Admin**")
        else:
            st.markdown("👤 **Usuário**")
    
    with col3:
        if st.button("🚪 Sair", use_container_width=True):
            GerenciadorAutenticacao.fazer_logout()

###########################################
# MÓDULO 1: CONFIGURAÇÃO DE CUSTOS
###########################################

def modulo_custos_despesas(sheets_manager):
    """Módulo de configuração de custos e despesas"""
    st.header("⚙️ Configuração de Custos e Despesas")
    
    prefix = st.session_state.get('prefix', '')
    config = sheets_manager.read_user_config(prefix)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 Custos Variáveis (%)")
        cust_var_impostos_pct = st.number_input(
            "Impostos (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_impostos_pct', 0))
        )
        cust_var_royalties_pct = st.number_input(
            "Royalties (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_royalties_pct', 0))
        )
        cust_var_gestao_pct = st.number_input(
            "Gestão (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_gestao_pct', 0))
        )
        cust_var_taxa_cartao_pct = st.number_input(
            "Taxa Cartão (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_taxa_cartao_pct', 0))
        )
        cust_var_repasse_condominio_pct = st.number_input(
            "Repasse Condomínio (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_repasse_condominio_pct', 0))
        )
        cust_var_investidor_pct = st.number_input(
            "Investidor (%)", min_value=0.0, max_value=100.0, step=0.1,
            value=float(config.get('cust_var_investidor_pct', 0))
        )
    
    with col2:
        st.subheader("🏢 Custos Fixos (R$)")
        cust_fix_monitoramento = st.number_input(
            "Monitoramento", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_monitoramento', 0))
        )
        cust_fix_combustivel = st.number_input(
            "Combustível", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_combustivel', 0))
        )
        cust_fix_totem = st.number_input(
            "Totem", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_totem', 0))
        )
        cust_fix_contabilidade = st.number_input(
            "Contabilidade", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_contabilidade', 0))
        )
        cust_fix_internet = st.number_input(
            "Internet", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_internet', 0))
        )
        cust_fix_telefone = st.number_input(
            "Telefone", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_telefone', 0))
        )
        cust_fix_seguro = st.number_input(
            "Seguro", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_seguro', 0))
        )
        cust_fix_folha = st.number_input(
            "Folha", min_value=0.0, step=100.0,
            value=float(config.get('cust_fix_folha', 0))
        )
        cust_fix_aluguel = st.number_input(
            "Aluguel", min_value=0.0, step=100.0,
            value=float(config.get('cust_fix_aluguel', 0))
        )
        cust_fix_outros = st.number_input(
            "Outros", min_value=0.0, step=10.0,
            value=float(config.get('cust_fix_outros', 0))
        )
    
    with col3:
        st.subheader("📊 Faturamento Base")
        faturamento_base = st.number_input(
            "Faturamento Mensal (R$)", min_value=0.0, step=1000.0,
            value=float(config.get('faturamento_base', 0))
        )
        
        st.markdown("---")
        st.subheader("📈 Resumo")
        
        total_var = sum([
            cust_var_impostos_pct, cust_var_royalties_pct, cust_var_gestao_pct,
            cust_var_taxa_cartao_pct, cust_var_repasse_condominio_pct, cust_var_investidor_pct
        ])
        
        total_fix = sum([
            cust_fix_monitoramento, cust_fix_combustivel, cust_fix_totem,
            cust_fix_contabilidade, cust_fix_internet, cust_fix_telefone,
            cust_fix_seguro, cust_fix_folha, cust_fix_aluguel, cust_fix_outros
        ])
        
        pct_fix = (total_fix / faturamento_base * 100) if faturamento_base > 0 else 0
        total_despesas = total_var + pct_fix
        
        st.metric("Custo Variável", f"{total_var:.2f}%")
        st.metric("Custo Fixo", f"R$ {total_fix:,.2f}")
        st.metric("% Fixo/Fat", f"{pct_fix:.2f}%")
        
        if total_despesas >= 100:
            st.error(f"⚠️ Total: {total_despesas:.2f}%")
        else:
            st.success(f"✅ Total: {total_despesas:.2f}%")
    
    st.markdown("---")
    if st.button("💾 Salvar Configuração", type="primary", use_container_width=True):
        nova_config = {
            'cust_var_impostos_pct': cust_var_impostos_pct,
            'cust_var_royalties_pct': cust_var_royalties_pct,
            'cust_var_gestao_pct': cust_var_gestao_pct,
            'cust_var_taxa_cartao_pct': cust_var_taxa_cartao_pct,
            'cust_var_repasse_condominio_pct': cust_var_repasse_condominio_pct,
            'cust_var_investidor_pct': cust_var_investidor_pct,
            'cust_fix_monitoramento': cust_fix_monitoramento,
            'cust_fix_combustivel': cust_fix_combustivel,
            'cust_fix_totem': cust_fix_totem,
            'cust_fix_contabilidade': cust_fix_contabilidade,
            'cust_fix_internet': cust_fix_internet,
            'cust_fix_telefone': cust_fix_telefone,
            'cust_fix_seguro': cust_fix_seguro,
            'cust_fix_folha': cust_fix_folha,
            'cust_fix_aluguel': cust_fix_aluguel,
            'cust_fix_outros': cust_fix_outros,
            'faturamento_base': faturamento_base
        }
        
        calc = CalculadoraMarkup()
        resultado = calc.calcular_markup_usuario(nova_config)
        
        if resultado['erro_markup']:
            st.error(resultado['erro_markup'])
        else:
            try:
                sheets_manager.write_user_config(prefix, nova_config)
                produtos_df = sheets_manager.read_user_products(prefix)
                if not produtos_df.empty:
                    produtos_atualizados = calc.recalcular_produtos(
                        produtos_df, resultado['markup_mult'], resultado['markup_divisor']
                    )
                    sheets_manager.write_user_products(prefix, produtos_atualizados)
                    st.success(f"✅ Configuração salva! {len(produtos_df)} produtos recalculados.")
                else:
                    st.success("✅ Configuração salva!")
                st.info(f"**Markup:** {resultado['markup_mult']:.4f}x")
            except Exception as e:
                st.error(f"Erro: {e}")

###########################################
# MÓDULO 2: CADASTRO DE PRODUTOS
###########################################

def modulo_cadastro_produtos(sheets_manager):
    """Módulo de cadastro e gerenciamento de produtos"""
    st.header("📦 Cadastro de Produtos")
    
    prefix = st.session_state.get('prefix', '')
    
    tabs = st.tabs(["📋 Listar Produtos", "➕ Adicionar Produto", "📥 Import/Export"])
    
    # TAB 1: LISTAR PRODUTOS
    with tabs[0]:
        produtos_df = sheets_manager.read_user_products(prefix)
        
        if produtos_df.empty:
            st.info("📭 Nenhum produto cadastrado ainda. Use a aba 'Adicionar Produto' ou importe um CSV.")
        else:
            st.markdown(f"**Total de produtos:** {len(produtos_df)}")
            
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_nome = st.text_input("🔍 Filtrar por nome:", "")
            with col_f2:
                categorias = ['Todas'] + sorted(produtos_df['categoria'].unique().tolist())
                filtro_cat = st.selectbox("Filtrar por categoria:", categorias)
            
            # Aplicar filtros
            df_filtrado = produtos_df.copy()
            if filtro_nome:
                df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(filtro_nome, case=False, na=False)]
            if filtro_cat != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['categoria'] == filtro_cat]
            
            # Exibir tabela
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[[
                        'codigo', 'nome', 'compra', 'desp_add', 'custo_total',
                        'preco_sugerido', 'preco_final', 'margem_liquida_estimada_pct', 'categoria'
                    ]],
                    use_container_width=True,
                    height=400
                )
                
                # Opção de deletar
                st.markdown("---")
                st.subheader("🗑️ Excluir Produto")
                codigo_deletar = st.text_input("Digite o código do produto para excluir:")
                if st.button("Deletar Produto", type="secondary"):
                    if codigo_deletar:
                        produtos_df = produtos_df[produtos_df['codigo'] != codigo_deletar]
                        sheets_manager.write_user_products(prefix, produtos_df)
                        st.success(f"Produto {codigo_deletar} excluído!")
                        st.rerun()
                    else:
                        st.warning("Digite um código válido")
            else:
                st.warning("Nenhum produto encontrado com os filtros aplicados")
    
    # TAB 2: ADICIONAR PRODUTO
    with tabs[1]:
        st.subheader("Adicionar Novo Produto")
        
        with st.form("form_add_produto"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                codigo = st.text_input("Código *", help="Código único do produto")
                nome = st.text_input("Nome *", help="Nome do produto")
                compra = st.number_input("Valor de Compra (R$) *", min_value=0.0, step=0.01)
                desp_add = st.number_input("Despesas Adicionais (R$)", min_value=0.0, step=0.01, value=0.0)
            
            with col_b:
                margem_desejada = st.number_input("Margem Desejada (%)", min_value=0.0, max_value=100.0, step=1.0, value=40.0)
                preco_final_input = st.number_input("Preço Final (R$) - Opcional", min_value=0.0, step=0.01, value=0.0, help="Deixe 0 para usar preço sugerido")
                categoria = st.text_input("Categoria", value="Geral")
                obs = st.text_area("Observações", "")
            
            submitted = st.form_submit_button("💾 Salvar Produto", type="primary", use_container_width=True)
            
            if submitted:
                if not codigo or not nome:
                    st.error("❌ Código e Nome são obrigatórios!")
                else:
                    # Verificar se código já existe
                    produtos_df = sheets_manager.read_user_products(prefix)
                    if not produtos_df.empty and codigo in produtos_df['codigo'].values:
                        st.error(f"❌ Código '{codigo}' já existe!")
                    else:
                        # Calcular preços
                        config = sheets_manager.read_user_config(prefix)
                        calc = CalculadoraMarkup()
                        resultado = calc.calcular_markup_usuario(config)
                        
                        if resultado['erro_markup']:
                            st.error(resultado['erro_markup'])
                        else:
                            novo_produto = {
                                'codigo': codigo,
                                'nome': nome,
                                'compra': compra,
                                'desp_add': desp_add,
                                'margem_desejada_pct': margem_desejada,
                                'preco_final': preco_final_input,
                                'categoria': categoria,
                                'obs': obs
                            }
                            
                            produto_calc = calc.calcular_produto(
                                novo_produto,
                                resultado['markup_mult'],
                                resultado['markup_divisor']
                            )
                            
                            # Adicionar ao DataFrame
                            novo_df = pd.DataFrame([produto_calc])
                            if produtos_df.empty:
                                produtos_final = novo_df
                            else:
                                produtos_final = pd.concat([produtos_df, novo_df], ignore_index=True)
                            
                            sheets_manager.write_user_products(prefix, produtos_final)
                            st.success(f"✅ Produto '{nome}' adicionado com sucesso!")
                            st.info(f"💰 Preço sugerido: R$ {produto_calc['preco_sugerido']:.2f}")
                            st.balloons()
    
    # TAB 3: IMPORT/EXPORT
    with tabs[2]:
        col_imp, col_exp = st.columns(2)
        
        with col_imp:
            st.subheader("📥 Importar CSV/XLSX")
            st.markdown("""
            **Formato esperado:**
            - codigo
            - nome
            - compra
            - desp_add
            - margem_desejada_pct (opcional)
            - preco_final (opcional)
            - categoria (opcional)
            - obs (opcional)
            """)
            
            uploaded = st.file_uploader("Selecione arquivo", type=['csv', 'xlsx'])
            
            if uploaded:
                try:
                    if uploaded.name.endswith('.csv'):
                        df_import = pd.read_csv(uploaded)
                    else:
                        df_import = pd.read_excel(uploaded)
                    
                    st.write("**Preview:**")
                    st.dataframe(df_import.head(), use_container_width=True)
                    
                    if st.button("✅ Confirmar Importação", type="primary"):
                        # Preencher campos opcionais
                        if 'margem_desejada_pct' not in df_import.columns:
                            df_import['margem_desejada_pct'] = 40.0
                        if 'preco_final' not in df_import.columns:
                            df_import['preco_final'] = 0.0
                        if 'categoria' not in df_import.columns:
                            df_import['categoria'] = 'Geral'
                        if 'obs' not in df_import.columns:
                            df_import['obs'] = ''
                        if 'desp_add' not in df_import.columns:
                            df_import['desp_add'] = 0.0
                        
                        # Recalcular preços
                        config = sheets_manager.read_user_config(prefix)
                        calc = CalculadoraMarkup()
                        resultado = calc.calcular_markup_usuario(config)
                        
                        if resultado['erro_markup']:
                            st.error(resultado['erro_markup'])
                        else:
                            df_recalc = calc.recalcular_produtos(
                                df_import,
                                resultado['markup_mult'],
                                resultado['markup_divisor']
                            )
                            
                            # Concatenar com existentes
                            produtos_df = sheets_manager.read_user_products(prefix)
                            if produtos_df.empty:
                                produtos_final = df_recalc
                            else:
                                produtos_final = pd.concat([produtos_df, df_recalc], ignore_index=True)
                            
                            sheets_manager.write_user_products(prefix, produtos_final)
                            st.success(f"✅ {len(df_import)} produtos importados com sucesso!")
                            st.balloons()
                
                except Exception as e:
                    st.error(f"Erro ao importar: {e}")
        
        with col_exp:
            st.subheader("📤 Exportar CSV")
            st.markdown("Baixe todos os produtos cadastrados em formato CSV.")
            
            produtos_df = sheets_manager.read_user_products(prefix)
            
            if produtos_df.empty:
                st.info("Nenhum produto para exportar")
            else:
                csv = produtos_df.to_csv(index=False)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                st.download_button(
                    label="⬇️ Baixar CSV",
                    data=csv,
                    file_name=f"produtos_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.success(f"✅ {len(produtos_df)} produtos disponíveis para download")

###########################################
# MÓDULO 3: RELATÓRIOS
###########################################

def modulo_relatorios(sheets_manager):
    """Módulo de relatórios e análise visual"""
    st.header("📊 Relatório de Precificação e Análise Visual")
    
    prefix = st.session_state.get('prefix', '')
    produtos_df = sheets_manager.read_user_products(prefix)
    config = sheets_manager.read_user_config(prefix)
    
    if produtos_df.empty:
        st.warning("📭 Nenhum produto cadastrado. Cadastre produtos para visualizar relatórios.")
        return
    
    # Seção 1: Tabela de Precificação
    st.subheader("📋 Tabela de Precificação")
    
    colunas_exibir = [
        'codigo', 'nome', 'custo_total', 'margem_desejada_pct',
        'preco_sugerido', 'preco_final', 'diferenca_final_vs_sugerido',
        'margem_liquida_estimada_pct', 'categoria'
    ]
    
    # Renomear colunas para melhor visualização
    df_display = produtos_df[colunas_exibir].copy()
    df_display.columns = [
        'Código', 'Nome', 'Custo Total', 'Margem Desejada (%)',
        'Preço Sugerido', 'Preço Final', 'Diferença (R$)',
        'Margem Líquida (%)', 'Categoria'
    ]
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Estatísticas rápidas
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Produtos", len(produtos_df))
    with col_s2:
        st.metric("Custo Médio", f"R$ {produtos_df['custo_total'].mean():.2f}")
    with col_s3:
        st.metric("Preço Médio", f"R$ {produtos_df['preco_final'].mean():.2f}")
    with col_s4:
        st.metric("Margem Média", f"{produtos_df['margem_liquida_estimada_pct'].mean():.2f}%")
    
    st.markdown("---")
    
    # Seção 2: Gráficos
    st.subheader("📈 Análises Visuais")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("### Composição Percentual da Precificação")
        calc = CalculadoraMarkup()
        resultado = calc.calcular_markup_usuario(config)
        
        gerador = GeradorGraficos()
        fig_doughnut = gerador.grafico_doughnut_composicao(resultado)
        st.plotly_chart(fig_doughnut, use_container_width=True)
        
        # Informações adicionais
        with st.expander("ℹ️ Detalhes do Markup"):
            st.markdown(f"""
            **Custos Variáveis:** {resultado['total_cust_var_pct']:.2f}%
            
            **Custos Fixos:** R$ {resultado['total_cust_fix']:,.2f}
            
            **% Custos Fixos/Fat:** {resultado['pct_cust_fix_sobre_fat']:.2f}%
            
            **Total Despesas:** {resultado['total_despesas_pct']:.2f}%
            
            **Markup Divisor:** {resultado['markup_divisor']:.4f}
            
            **Markup Multiplicador:** {resultado['markup_mult']:.4f}x
            """)
    
    with col_g2:
        st.markdown("### Custo Total vs. Preço de Venda Final")
        
        # Controle de produtos exibidos
        num_produtos = st.slider(
            "Número de produtos a exibir:",
            min_value=5,
            max_value=min(50, len(produtos_df)),
            value=min(10, len(produtos_df)),
            key="slider_produtos_relatorio"
        )
        
        fig_barras = gerador.grafico_barras_comparativo(produtos_df, limite=num_produtos)
        st.plotly_chart(fig_barras, use_container_width=True)

###########################################
# MÓDULO 4: DASHBOARD
###########################################

def modulo_dashboard(sheets_manager):
    """Módulo de dashboard gerencial e KPIs"""
    st.header("📈 Dashboard Gerencial e KPIs de Rentabilidade")
    
    prefix = st.session_state.get('prefix', '')
    produtos_df = sheets_manager.read_user_products(prefix)
    config = sheets_manager.read_user_config(prefix)
    
    if produtos_df.empty:
        st.warning("📭 Nenhum produto cadastrado. Cadastre produtos para visualizar KPIs.")
        return
    
    # Calcular KPIs
    calc = CalculadoraMarkup()
    kpis = calc.calcular_kpis(produtos_df, config)
    
    # Seção 1: KPIs Principais
    st.subheader("🎯 KPIs Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis['margem_media_desejada']:.2f}%</div>
            <div class="kpi-label">Margem Média Desejada</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis['margem_liquida_estimada']:.2f}%</div>
            <div class="kpi-label">Margem Líquida Estimada</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        lucro_color = "#22c55e" if kpis['lucro_total_estimado'] >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {lucro_color};">R$ {kpis['lucro_total_estimado']:,.2f}</div>
            <div class="kpi-label">Lucro Total Estimado (Base Mês)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis['produtos_cadastrados']}</div>
            <div class="kpi-label">Produtos Cadastrados</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seção 2: Análise de Rentabilidade
    st.subheader("💰 Análise de Rentabilidade")
    
    col_rent1, col_rent2 = st.columns(2)
    
    with col_rent1:
        st.markdown("### 🟢 Produtos Mais Rentáveis")
        
        # Calcular lucro por produto
        produtos_df['lucro_unitario'] = produtos_df['preco_final'] - produtos_df['custo_total']
        
        top_rentaveis = produtos_df.nlargest(10, 'margem_liquida_estimada_pct')
        
        for idx, row in top_rentaveis.iterrows():
            st.success(f"""
            **{row['nome']}** ({row['codigo']})
            - Margem: {row['margem_liquida_estimada_pct']:.2f}%
            - Lucro Unit.: R$ {row['lucro_unitario']:.2f}
            """)
    
    with col_rent2:
        st.markdown("### 🔴 Produtos Menos Rentáveis (Atenção)")
        
        bottom_rentaveis = produtos_df.nsmallest(10, 'margem_liquida_estimada_pct')
        
        for idx, row in bottom_rentaveis.iterrows():
            st.error(f"""
            **{row['nome']}** ({row['codigo']})
            - Margem: {row['margem_liquida_estimada_pct']:.2f}%
            - Lucro Unit.: R$ {row['lucro_unitario']:.2f}
            """)
    
    st.markdown("---")
    
    # Seção 3: Análise por Categoria
    st.subheader("📊 Margem por Categoria")
    
    col_cat1, col_cat2 = st.columns([2, 1])
    
    with col_cat1:
        gerador = GeradorGraficos()
        fig_categoria = gerador.grafico_margem_categoria(produtos_df)
        st.plotly_chart(fig_categoria, use_container_width=True)
    
    with col_cat2:
        st.markdown("### 📋 Resumo por Categoria")
        
        if 'categoria' in produtos_df.columns:
            resumo_cat = produtos_df.groupby('categoria').agg({
                'codigo': 'count',
                'margem_liquida_estimada_pct': 'mean',
                'lucro_unitario': 'sum'
            }).round(2)
            
            resumo_cat.columns = ['Produtos', 'Margem Média (%)', 'Lucro Total (R$)']
            st.dataframe(resumo_cat, use_container_width=True)
    
    st.markdown("---")
    
    # Seção 4: Recomendações
    st.subheader("💡 Recomendações")
    
    # Produtos com margem baixa
    produtos_baixa_margem = produtos_df[produtos_df['margem_liquida_estimada_pct'] < 20]
    if not produtos_baixa_margem.empty:
        st.warning(f"""
        ⚠️ **{len(produtos_baixa_margem)} produtos** com margem abaixo de 20%.
        Considere ajustar preços ou revisar custos.
        """)
    
    # Produtos com diferença grande entre sugerido e final
    produtos_df['dif_abs'] = abs(produtos_df['diferenca_final_vs_sugerido'])
    produtos_grande_dif = produtos_df[produtos_df['dif_abs'] > produtos_df['preco_sugerido'] * 0.2]
    if not produtos_grande_dif.empty:
        st.info(f"""
        ℹ️ **{len(produtos_grande_dif)} produtos** com diferença > 20% entre preço sugerido e final.
        Revise se os preços finais estão alinhados com a estratégia.
        """)

###########################################
# FUNÇÃO PRINCIPAL
###########################################

def main():
    """Função principal da aplicação"""
    
    # Inicializar conexão
    sheets_manager = inicializar_conexao()
    
    # Verificar autenticação
    if not GerenciadorAutenticacao.verificar_autenticacao():
        GerenciadorAutenticacao.fazer_login(sheets_manager)
        return
    
    # Usuário autenticado - exibir interface principal
    exibir_header()
    exibir_info_usuario()
    
    st.markdown("---")
    
    # Sidebar de navegação
    with st.sidebar:
        st.title("📋 Menu Principal")
        st.markdown("---")
        
        # Logo ou identidade visual (opcional)
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #9333ea;">NMP</h2>
            <p style="color: #666; font-size: 0.8rem;">Sistema de Precificação</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menu de navegação
        opcao = st.radio(
            "Navegação:",
            [
                "⚙️ Custos e Despesas",
                "📦 Cadastro de Produtos",
                "📊 Relatórios",
                "📈 Dashboard"
            ],
            key="menu_principal"
        )
        
        st.markdown("---")
        
        # Informações do usuário
        st.caption(f"👤 {st.session_state.get('display_name')}")
        st.caption(f"🔑 {st.session_state.get('role').upper()}")
        
        # Versão
        st.markdown("---")
        st.caption("v1.0.0 | © 2025 NMP")
    
    # Roteamento baseado na opção selecionada
    if opcao == "⚙️ Custos e Despesas":
        modulo_custos_despesas(sheets_manager)
    
    elif opcao == "📦 Cadastro de Produtos":
        modulo_cadastro_produtos(sheets_manager)
    
    elif opcao == "📊 Relatórios":
        modulo_relatorios(sheets_manager)
    
    elif opcao == "📈 Dashboard":
        modulo_dashboard(sheets_manager)

# Executar aplicação
if __name__ == "__main__":
    main()
