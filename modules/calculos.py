"""
Módulo de Cálculos de Markup e Precificação
Implementa todas as fórmulas e validações
"""
import pandas as pd
from typing import Dict, Tuple

class CalculadoraMarkup:
    """Calculadora de Markup e Precificação"""
    
    @staticmethod
    def calcular_markup_usuario(config: Dict[str, float]) -> Dict[str, float]:
        # Cálculos de markup conforme regras do projeto
        total_cust_var_pct = (
            config.get('cust_var_impostos_pct', 0) +
            config.get('cust_var_royalties_pct', 0) +
            config.get('cust_var_gestao_pct', 0) +
            config.get('cust_var_taxa_cartao_pct', 0) +
            config.get('cust_var_repasse_condominio_pct', 0) +
            config.get('cust_var_investidor_pct', 0)
        )
        total_cust_fix = (
            config.get('cust_fix_monitoramento', 0) +
            config.get('cust_fix_combustivel', 0) +
            config.get('cust_fix_totem', 0) +
            config.get('cust_fix_contabilidade', 0) +
            config.get('cust_fix_internet', 0) +
            config.get('cust_fix_telefone', 0) +
            config.get('cust_fix_seguro', 0) +
            config.get('cust_fix_folha', 0) +
            config.get('cust_fix_aluguel', 0) +
            config.get('cust_fix_outros', 0)
        )
        faturamento_base = config.get('faturamento_base', 0)
        if faturamento_base > 0:
            pct_cust_fix_sobre_fat = (total_cust_fix / faturamento_base) * 100
        else:
            pct_cust_fix_sobre_fat = 0
        total_despesas_pct = total_cust_var_pct + pct_cust_fix_sobre_fat
        markup_divisor = 1 - (total_despesas_pct / 100)
        if markup_divisor > 0:
            markup_mult = 1 / markup_divisor
            erro_markup = None
        else:
            markup_mult = 0
            erro_markup = f"ERRO: Markup divisor é {markup_divisor:.4f}. Total de despesas ({total_despesas_pct:.2f}%) >= 100% do faturamento."
        return {
            'total_cust_var_pct': total_cust_var_pct,
            'total_cust_fix': total_cust_fix,
            'pct_cust_fix_sobre_fat': pct_cust_fix_sobre_fat,
            'total_despesas_pct': total_despesas_pct,
            'markup_divisor': markup_divisor,
            'markup_mult': markup_mult,
            'erro_markup': erro_markup,
            'faturamento_base': faturamento_base
        }
    
    @staticmethod
    def calcular_produto(produto: Dict, markup_mult: float, markup_divisor: float) -> Dict:
        compra = float(produto.get('compra', 0))
        desp_add = float(produto.get('desp_add', 0))
        custo_total = compra + desp_add
        markup_divisor_pct = round(markup_divisor * 100, 4)
        preco_sugerido = round(custo_total * markup_mult, 2)
        preco_final = float(produto.get('preco_final', 0))
        if preco_final <= 0:
            preco_final = preco_sugerido
        diferenca_final_vs_sugerido = round(preco_final - preco_sugerido, 2)
        if preco_final > 0:
            margem_liquida_estimada_pct = round(
                ((preco_final - custo_total) / preco_final) * 100, 2
            )
        else:
            margem_liquida_estimada_pct = 0
        produto_atualizado = produto.copy()
        produto_atualizado.update({
            'custo_total': custo_total,
            'markup_divisor_pct': markup_divisor_pct,
            'markup_mult': markup_mult,
            'preco_sugerido': preco_sugerido,
            'preco_final': preco_final,
            'diferenca_final_vs_sugerido': diferenca_final_vs_sugerido,
            'margem_liquida_estimada_pct': margem_liquida_estimada_pct
        })
        return produto_atualizado
    
    @staticmethod
    def recalcular_produtos(produtos_df: pd.DataFrame, markup_mult: float, markup_divisor: float) -> pd.DataFrame:
        if produtos_df.empty:
            return produtos_df
        calc = CalculadoraMarkup()
        produtos_recalculados = []
        for _, row in produtos_df.iterrows():
            produto_dict = row.to_dict()
            produto_atualizado = calc.calcular_produto(produto_dict, markup_mult, markup_divisor)
            produtos_recalculados.append(produto_atualizado)
        return pd.DataFrame(produtos_recalculados)
    
    @staticmethod
    def validar_config(config: Dict[str, float]) -> Tuple[bool, str]:
        faturamento_base = config.get('faturamento_base', 0)
        if faturamento_base <= 0:
            return False, "⚠️ AVISO: Faturamento base não definido ou zero. Custos fixos não serão considerados."
        resultado = CalculadoraMarkup.calcular_markup_usuario(config)
        if resultado['markup_divisor'] <= 0:
            return False, resultado['erro_markup']
        return True, "✅ Configuração válida"
    
    @staticmethod
    def calcular_kpis(produtos_df: pd.DataFrame, config: Dict) -> Dict:
        if produtos_df.empty:
            return {
                'margem_media_desejada': 0,
                'margem_liquida_estimada': 0,
                'lucro_total_estimado': 0,
                'produtos_cadastrados': 0
            }
        margem_media_desejada = produtos_df['margem_desejada_pct'].mean() if 'margem_desejada_pct' in produtos_df.columns else 0
        margem_liquida_estimada = produtos_df['margem_liquida_estimada_pct'].mean() if 'margem_liquida_estimada_pct' in produtos_df.columns else 0
        if 'preco_final' in produtos_df.columns and 'custo_total' in produtos_df.columns:
            lucro_total_estimado = (produtos_df['preco_final'] - produtos_df['custo_total']).sum()
        else:
            lucro_total_estimado = 0
        produtos_cadastrados = len(produtos_df)
        return {
            'margem_media_desejada': round(margem_media_desejada, 2),
            'margem_liquida_estimada': round(margem_liquida_estimada, 2),
            'lucro_total_estimado': round(lucro_total_estimado, 2),
            'produtos_cadastrados': produtos_cadastrados
        }
