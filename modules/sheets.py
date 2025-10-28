"""
Módulo de Comunicação com Google Sheets API
Gerencia leitura e escrita de dados na planilha
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any

class SheetsManager:
    """Gerenciador de operações com Google Sheets"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, spreadsheet_id: str, credentials_info: Dict):
        """
        Inicializa conexão com Google Sheets
        
        Args:
            spreadsheet_id: ID da planilha do Google Sheets
            credentials_info: Dicionário com credenciais da service account
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=self.SCOPES
        )
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = None
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com a planilha"""
        try:
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        except Exception as e:
            st.error(f"Erro ao conectar com Google Sheets: {e}")
            raise
    
    def _get_or_create_worksheet(self, title: str, rows: int = 1000, cols: int = 20) -> gspread.Worksheet:
        """Obtém worksheet ou cria se não existir"""
        try:
            return self.spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
    
    def read_worksheet_to_df(self, worksheet_name: str) -> pd.DataFrame:
        """
        Lê worksheet e retorna como DataFrame
        
        Args:
            worksheet_name: Nome da aba
            
        Returns:
            DataFrame com dados da aba
        """
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except gspread.WorksheetNotFound:
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Erro ao ler aba '{worksheet_name}': {e}")
            return pd.DataFrame()
    
    def write_df_to_worksheet(self, df: pd.DataFrame, worksheet_name: str, clear_first: bool = True):
        """
        Escreve DataFrame para worksheet
        
        Args:
            df: DataFrame para escrever
            worksheet_name: Nome da aba
            clear_first: Se True, limpa aba antes de escrever
        """
        try:
            worksheet = self._get_or_create_worksheet(worksheet_name)
            
            if clear_first:
                worksheet.clear()
            
            # Converter DataFrame para lista de listas
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Escrever dados em batch
            worksheet.update('A1', data)
            
        except Exception as e:
            st.error(f"Erro ao escrever na aba '{worksheet_name}': {e}")
            raise
    
    def read_users(self) -> pd.DataFrame:
        """Lê aba de usuários"""
        return self.read_worksheet_to_df('users')
    
    def read_user_config(self, prefix: str) -> Dict[str, Any]:
        """
        Lê configuração do usuário
        
        Args:
            prefix: Prefixo da aba do usuário
            
        Returns:
            Dicionário com configuração
        """
        config_name = f"{prefix}config"
        df = self.read_worksheet_to_df(config_name)
        
        if df.empty:
            return self._get_default_config()
        
        return df.iloc[0].to_dict() if not df.empty else self._get_default_config()
    
    def write_user_config(self, prefix: str, config: Dict[str, Any]):
        """
        Escreve configuração do usuário
        
        Args:
            prefix: Prefixo da aba do usuário
            config: Dicionário com configuração
        """
        config_name = f"{prefix}config"
        df = pd.DataFrame([config])
        self.write_df_to_worksheet(df, config_name, clear_first=True)
    
    def read_user_products(self, prefix: str) -> pd.DataFrame:
        """
        Lê produtos do usuário
        
        Args:
            prefix: Prefixo da aba do usuário
            
        Returns:
            DataFrame com produtos
        """
        products_name = f"{prefix}products"
        return self.read_worksheet_to_df(products_name)
    
    def write_user_products(self, prefix: str, products_df: pd.DataFrame):
        """
        Escreve produtos do usuário
        
        Args:
            prefix: Prefixo da aba do usuário
            products_df: DataFrame com produtos
        """
        products_name = f"{prefix}products"
        self.write_df_to_worksheet(products_df, products_name, clear_first=True)
    
    def _get_default_config(self) -> Dict[str, float]:
        """Retorna configuração padrão"""
        return {
            'cust_var_impostos_pct': 0.0,
            'cust_var_royalties_pct': 0.0,
            'cust_var_gestao_pct': 0.0,
            'cust_var_taxa_cartao_pct': 0.0,
            'cust_var_repasse_condominio_pct': 0.0,
            'cust_var_investidor_pct': 0.0,
            'cust_fix_monitoramento': 0.0,
            'cust_fix_combustivel': 0.0,
            'cust_fix_totem': 0.0,
            'cust_fix_contabilidade': 0.0,
            'cust_fix_internet': 0.0,
            'cust_fix_telefone': 0.0,
            'cust_fix_seguro': 0.0,
            'cust_fix_folha': 0.0,
            'cust_fix_aluguel': 0.0,
            'cust_fix_outros': 0.0,
            'faturamento_base': 0.0
        }
    
    def initialize_user_sheets(self, prefix: str):
        """
        Inicializa abas do usuário com valores padrão
        
        Args:
            prefix: Prefixo da aba do usuário
        """
        # Criar aba de config se não existir
        config_name = f"{prefix}config"
        df_config = self.read_worksheet_to_df(config_name)
        if df_config.empty:
            default_config = self._get_default_config()
            self.write_user_config(prefix, default_config)
        
        # Criar aba de products se não existir
        products_name = f"{prefix}products"
        df_products = self.read_worksheet_to_df(products_name)
        if df_products.empty:
            empty_products = pd.DataFrame(columns=[
                'codigo', 'nome', 'compra', 'desp_add', 'custo_total',
                'margem_desejada_pct', 'markup_divisor_pct', 'markup_mult',
                'preco_sugerido', 'preco_final', 'categoria', 'obs'
            ])
            self.write_user_products(prefix, empty_products)
