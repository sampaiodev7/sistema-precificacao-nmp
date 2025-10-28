"""
Módulo de Autenticação
Gerencia login e controle de acesso
"""
import bcrypt
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Tuple

class GerenciadorAutenticacao:
    """Gerenciador de autenticação de usuários"""
    
    @staticmethod
    def verificar_senha(senha: str, hash_armazenado: str) -> bool:
        """Verifica se senha corresponde ao hash bcrypt"""
        try:
            return bcrypt.checkpw(
                senha.encode('utf-8'),
                hash_armazenado.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def autenticar_usuario(
        username: str,
        senha: str,
        users_df: pd.DataFrame
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Autentica usuário"""
        user_row = users_df[users_df['user_id'] == username]
        
        if user_row.empty:
            return False, None, "Usuário não encontrado"
        
        user_data = user_row.iloc[0].to_dict()
        
        if not user_data.get('active', False):
            return False, None, "Usuário desativado"
        
        password_hash = user_data.get('password_hash', '')
        if not GerenciadorAutenticacao.verificar_senha(senha, password_hash):
            return False, None, "Senha incorreta"
        
        return True, user_data, None
    
    @staticmethod
    def fazer_login(sheets_manager):
        """Exibe formulário de login e gerencia sessão"""
        st.title("🔐 Sistema de Precificação Estratégica")
        st.markdown("### Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if not username or not password:
                    st.error("Por favor, preencha usuário e senha")
                    return
                
                users_df = sheets_manager.read_users()
                
                if users_df.empty:
                    st.error("Nenhum usuário cadastrado no sistema")
                    return
                
                autenticado, user_data, erro = GerenciadorAutenticacao.autenticar_usuario(
                    username, password, users_df
                )
                
                if autenticado:
                    st.session_state['authenticated'] = True
                    st.session_state['user_data'] = user_data
                    st.session_state['username'] = user_data['user_id']
                    st.session_state['display_name'] = user_data['display_name']
                    st.session_state['role'] = user_data['role']
                    st.session_state['prefix'] = user_data['sheet_tab_prefix']
                    
                    sheets_manager.initialize_user_sheets(user_data['sheet_tab_prefix'])
                    
                    st.success(f"Bem-vindo, {user_data['display_name']}!")
                    st.rerun()
                else:
                    st.error(f"Erro: {erro}")
        
        with st.expander("ℹ️ Instruções"):
            st.markdown("""
            **Primeiro acesso?**
            
            1. Solicite suas credenciais ao administrador do sistema
            2. Use seu ID de usuário e senha fornecidos
            3. Após o login, você terá acesso ao sistema de precificação
            
            **Esqueceu a senha?**
            
            Entre em contato com o administrador do sistema.
            """)
    
    @staticmethod
    def fazer_logout():
        """Faz logout do usuário"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    @staticmethod
    def verificar_autenticacao() -> bool:
        """Verifica se usuário está autenticado"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def obter_dados_usuario() -> Optional[Dict]:
        """Obtém dados do usuário da sessão"""
        if GerenciadorAutenticacao.verificar_autenticacao():
            return st.session_state.get('user_data')
        return None
    
    @staticmethod
    def e_admin() -> bool:
        """Verifica se usuário é admin"""
        if GerenciadorAutenticacao.verificar_autenticacao():
            return st.session_state.get('role') == 'admin'
        return False
