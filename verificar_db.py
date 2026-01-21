import sqlite3

# Conecta no banco de dados
conn = sqlite3.connect("emails_auto.db")
cursor = conn.cursor()

# Pega o e-mail e a senha de todos os agendamentos
cursor.execute("SELECT id, remetente, senha FROM agendamentos")
itens = cursor.fetchall()
conn.close()

print("\n--- ESPIANDO O BANCO DE DADOS ---")
if not itens:
    print("O banco está vazio.")
else:
    for item in itens:
        id_item, email, senha = item
        print(f"ID: {id_item}")
        print(f"E-mail: {email}")
        print(f"Senha Gravada: {senha}")
        print("-" * 30)

print("\nCONCLUSÃO:")
print("Se a senha acima for um monte de letras aleatórias (tipo 'gAAAA...'), está CRIPTOGRAFADO! 🔒")
print("Se você conseguir ler sua senha real, ela ainda está em Texto Puro. ⚠️")