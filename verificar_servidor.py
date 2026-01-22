import sqlite3
import os
from cryptography.fernet import Fernet
import platform

# ==============================================================================
# CONFIGURAÇÕES DOS DOIS MUNDOS
# ==============================================================================

# 1. AMBIENTE LOCAL (Seu PC)
LOCAL_DB = "emails_auto.db"
LOCAL_KEY = "secret.key"

# 2. AMBIENTE SERVIDOR (Simulação ou Real)
# Tenta achar a pasta SERVER_FAKE (simulação) ou usa S:\Automacao_Email (real)
if os.path.exists("SERVER_FAKE"):
    PASTA_SERV = "SERVER_FAKE"
##elif os.path.exists(r"S:\Automacao_Email"):
##    PASTA_SERV = r"S:\Automacao_Email"
else:
    PASTA_SERV = None 

SERV_DB = os.path.join(PASTA_SERV, "emails_central.db") if PASTA_SERV else None
SERV_KEY = os.path.join(PASTA_SERV, "chave_mestra.key") if PASTA_SERV else None

# ==============================================================================
# FERRAMENTAS
# ==============================================================================

def limpar_terminal():
    sistema = platform.system()
    if sistema == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def descriptografar(cipher, texto_cripto):
    try:
        return cipher.decrypt(texto_cripto.encode()).decode(), "🔓 SUCESSO"
    except:
        return "[ERRO NA CHAVE]", "🔒 FALHA"

def auditar_ambiente(nome_ambiente, arquivo_db, arquivo_key):
    print("\n" + "█"*80)
    print(f"🔍 AUDITANDO: {nome_ambiente}")
    print(f"   📂 Arquivo: {arquivo_db}")
    print("█"*80)

    # 1. Checa existência
    if not os.path.exists(arquivo_db):
        print(f"❌ Banco de dados não encontrado neste local.")
        return
    if not os.path.exists(arquivo_key):
        print(f"❌ Chave de segurança não encontrada neste local.")
        return

    # 2. Carrega chave
    try:
        with open(arquivo_key, "rb") as k:
            chave = k.read()
        cipher = Fernet(chave)
    except Exception as e:
        print(f"❌ Erro ao ler a chave: {e}")
        return

    # 3. Lê o Banco
    conn = sqlite3.connect(arquivo_db)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM agendamentos")
        colunas = [description[0] for description in cursor.description]
        linhas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Erro ao ler tabela: {e}")
        conn.close()
        return

    if not linhas:
        print("📭 O banco está VAZIO.")
        conn.close()
        return

    # 4. Exibe os dados
    print(f"✅ Encontrados {len(linhas)} agendamentos:\n")

    for linha in linhas:
        dados = dict(zip(colunas, linha))
        
        id_bd = dados.get('id', '?')
        reme = dados.get('remetente', 'Desconhecido')
        dest = dados.get('destinatario', 'Desconhecido')
        senha_cripto = dados.get('senha', '')
        dono = dados.get('dono', 'N/A (Local)')

        # Decifra a senha
        senha_real, status = descriptografar(cipher, senha_cripto)

        print(f"🆔 ID #{id_bd} | Criado por: 👤 {dono}")
        print(f"   📧 De: {reme}")
        print(f"   📨 Para: {dest}")
        print(f"   💾 Cripto: {senha_cripto}")  # <--- AGORA MOSTRA O HASH
        print(f"   🔑 Real:   {senha_real} ({status})")
        print("-" * 80)

    conn.close()

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    limpar_terminal()
    print("INICIANDO AUDITORIA V2.0... (Limpando histórico)")
    
    # 1. Audita o Local
    auditar_ambiente("AMBIENTE LOCAL (Seu PC)", LOCAL_DB, LOCAL_KEY)
    
    # 2. Audita o Servidor
    if PASTA_SERV:
        auditar_ambiente("AMBIENTE SERVIDOR (Compartilhado)", SERV_DB, SERV_KEY)
    else:
        print("\n" + "█"*80)
        print("⚠️ AMBIENTE SERVIDOR NÃO ENCONTRADO")
        print("█"*80)
    
    print("\n✅ Fim da Auditoria.")
    input("\nPressione ENTER para sair...")