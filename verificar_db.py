import sqlite3
import os
from cryptography.fernet import Fernet
import time

# --- CONFIGURAÇÕES ---
ARQUIVO_DB = "emails_auto.db"
ARQUIVO_KEY = "secret.key"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_chave():
    if not os.path.exists(ARQUIVO_KEY):
        print(f"❌ ERRO: O arquivo '{ARQUIVO_KEY}' não foi encontrado.")
        print("Certifique-se de que ele está na mesma pasta desse script.")
        exit()
    with open(ARQUIVO_KEY, "rb") as k:
        return k.read()

# ==============================================================================
# PARTE 1: AULA PRÁTICA (Simulação)
# ==============================================================================
def demonstrar_processo(cipher):
    print("\n" + "="*60)
    print("🔬 PARTE 1: ENTENDENDO A CRIPTOGRAFIA (SIMULAÇÃO)")
    print("="*60)
    
    senha_original = "MinhaSenhaSuperSecreta123"
    print(f"1. Temos uma senha original (Texto Plano):")
    print(f"   -> '{senha_original}'")
    time.sleep(1)

    print(f"\n2. O Python transforma texto em Bytes (Binário):")
    senha_bytes = senha_original.encode()
    print(f"   -> {senha_bytes}")
    time.sleep(1)

    print(f"\n3. A chave 'secret.key' mistura tudo (Encriptação):")
    senha_cripto = cipher.encrypt(senha_bytes)
    print(f"   -> {senha_cripto}")
    print("   (É ISSO que salvamos no banco de dados. Impossível ler sem a chave.)")
    time.sleep(1)

    print(f"\n4. Para ler, usamos a chave para desfazer a mistura (Decriptação):")
    senha_decriptada_bytes = cipher.decrypt(senha_cripto)
    senha_final = senha_decriptada_bytes.decode()
    print(f"   -> '{senha_final}'")
    
    print("\n✅ Conclusão: A senha original é igual a final? ", senha_original == senha_final)
    print("-" * 60)
    input("\nPressione ENTER para ver os dados REAIS do seu Banco de Dados...")

# ==============================================================================
# PARTE 2: DADOS REAIS DO BANCO
# ==============================================================================
def ler_banco_real(cipher):
    limpar_tela()
    print("\n" + "="*60)
    print(f"📂 PARTE 2: LENDO O ARQUIVO '{ARQUIVO_DB}'")
    print("="*60)

    if not os.path.exists(ARQUIVO_DB):
        print(f"❌ O arquivo {ARQUIVO_DB} não existe ou ainda não foi criado.")
        return

    conn = sqlite3.connect(ARQUIVO_DB)
    cursor = conn.cursor()

    # Selecionamos apenas colunas importantes para visualização
    try:
        cursor.execute("SELECT id, remetente, destinatario, senha FROM agendamentos")
        linhas = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao ler tabela: {e}")
        return

    if not linhas:
        print("📭 O banco de dados está vazio! Cadastre algo no sistema primeiro.")
    
    for linha in linhas:
        id_bd, remetente, destinatario, senha_criptografada = linha
        
        # Tentativa de descriptografar a senha do banco
        try:
            senha_real = cipher.decrypt(senha_criptografada.encode()).decode()
            status_cadeado = "🔓 SUCESSO"
            cor_senha = senha_real
        except Exception as e:
            status_cadeado = "🔒 ERRO (Chave incorreta?)"
            cor_senha = f"[Erro: {e}]"

        print(f"\n🆔 AGENDAMENTO #{id_bd}")
        print(f"   📧 De: {remetente}")
        print(f"   📨 Para: {destinatario}")
        print(f"   💾 No Banco (Criptografado): {senha_criptografada}")
        print(f"   👁️ Visão do Robô (Real):      {cor_senha}  <-- {status_cadeado}")
        print("." * 60)

    conn.close()

# ==============================================================================
# EXECUÇÃO
# ==============================================================================
if __name__ == "__main__":
    limpar_tela()
    chave_bytes = carregar_chave()
    motor_cripto = Fernet(chave_bytes)
    
    demonstrar_processo(motor_cripto)
    ler_banco_real(motor_cripto)
    
    print("\nFim da auditoria.")