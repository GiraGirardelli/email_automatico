import smtplib
from email.message import EmailMessage

# --- SEUS DADOS ---
# Preencha com cuidado
EMAIL_ORIGEM = "pedro.vidal@mediphacos.com.br"  # Sua conta Locaweb
SENHA_ORIGEM = "Pedro2014@"               # Sua senha normal da Locaweb
EMAIL_DESTINO = "pedrohgcvidal@gmail.com" # <--- COLOQUE SEU GMAIL AQUI

def testar_envio():
    print("--- INICIANDO TESTE DE ENVIO ---")
    
    # 1. Configurando a mensagem
    msg = EmailMessage()
    msg['Subject'] = "Teste de Python para Gmail"
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = EMAIL_DESTINO
    msg.set_content("""
    Olá!
    
    Se você recebeu este e-mail no seu Gmail, parabéns!
    Isso significa que o script Python autenticou na Locaweb e disparou a mensagem com sucesso.
    
    Att,
    Seu Robô Python
    """)

    # 2. Conectando e Enviando
    try:
        print(f"Conectando ao servidor da Locaweb (email-ssl.com.br)...")
        
        with smtplib.SMTP_SSL('email-ssl.com.br', 465) as smtp:
            smtp.login(EMAIL_ORIGEM, SENHA_ORIGEM)
            smtp.send_message(msg)
            
        print(f"✅ SUCESSO! E-mail enviado de {EMAIL_ORIGEM} para {EMAIL_DESTINO}")
        print("Corre lá no seu Gmail e veja se chegou (olhe a caixa de Spam também).")
        
    except Exception as e:
        print(f"❌ ERRO AO ENVIAR: {e}")

if __name__ == "__main__":
    testar_envio()