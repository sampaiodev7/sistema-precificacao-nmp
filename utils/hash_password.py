#!/usr/bin/env python3
"""
Script para gerar hash bcrypt de senhas
Uso: python utils/hash_password.py
"""
import bcrypt
import getpass

def gerar_hash(senha):
    """Gera hash bcrypt de uma senha"""
    salt = bcrypt.gensalt(rounds=12)
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_senha.decode('utf-8')

def verificar_senha(senha, hash_armazenado):
    """Verifica se senha corresponde ao hash"""
    return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 GERADOR DE HASH BCRYPT PARA SENHAS")
    print("=" * 60)
    
    while True:
        print("\n1. Gerar novo hash")
        print("2. Verificar senha contra hash")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            senha = getpass.getpass("\nDigite a senha: ")
            confirma = getpass.getpass("Confirme a senha: ")
            
            if senha == confirma:
                hash_gerado = gerar_hash(senha)
                print("\n" + "=" * 60)
                print("✅ Hash gerado com sucesso!")
                print("=" * 60)
                print(f"\n{hash_gerado}")
                print("\n" + "=" * 60)
                print("📋 Copie este hash para a coluna 'password_hash'")
                print("   na aba 'users' do Google Sheets")
                print("=" * 60)
            else:
                print("\n❌ Senhas não conferem!")
                
        elif opcao == "2":
            senha = getpass.getpass("\nDigite a senha: ")
            hash_armazenado = input("Digite o hash armazenado: ").strip()
            
            try:
                if verificar_senha(senha, hash_armazenado):
                    print("\n✅ Senha CORRETA!")
                else:
                    print("\n❌ Senha INCORRETA!")
            except Exception as e:
                print(f"\n❌ Erro ao verificar: {e}")
                
        elif opcao == "3":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
