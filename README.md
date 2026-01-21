# 📧 Super Agendador de E-mails (V9.0)

Um sistema completo e seguro de automação de e-mails desenvolvido em Python. Permite agendar envios únicos, diários, semanais, mensais ou anuais, com suporte a anexos, importação em massa via Excel e criptografia de senhas.

---

## 🚀 Funcionalidades

* **Agendamento Universal:**
    * 📅 **Diário:** Envia todo dia.
    * 🗓️ **Semanal:** Envia em um dia específico da semana (ex: toda Terça).
    * 📆 **Mensal:** Envia em um dia fixo do mês (ex: todo dia 10).
    * 🎉 **Anual:** Envia em uma data específica todo ano (ex: Aniversários).
    * 🎯 **Único:** Envia uma vez e **se auto-destrói** do banco de dados após o sucesso.
* **Interface Gráfica Moderna:** Desenvolvida com `CustomTkinter` (Modo Dark).
* **Segurança Militar:** As senhas são criptografadas (Hash) antes de serem salvas no banco de dados (`secret.key`).
* **Importação em Massa:** Carregue listas de clientes via Excel (`.xlsx`).
* **Histórico Visual:** Logs de sucesso e erro com cartões coloridos e detalhes do envio.
* **Modo Fantasma:** Roda em segundo plano sem abrir janelas (usando `pythonw`).

---

## 🛠️ Pré-requisitos

Certifique-se de ter o Python instalado. Instale as dependências necessárias com o comando:

```bash
pip install customtkinter pandas cryptography openpyxl
```
## ⚙️ Como Configurar o Robô (Windows)

Para que o sistema funcione automaticamente, é necessário configurar o **Agendador de Tarefas do Windows**. Siga estes passos rigorosamente:

### 1. Criar a Tarefa Básica
1. Abra o **Agendador de Tarefas**.
2. Clique em **Criar Tarefa**.
3. **Nome:** `RoboEmail` (ou outro de sua preferência).
4. **Aba Geral:**
   * Marque: `Executar estando o usuário conectado ou não`.
   * Marque: `Executar com privilégios mais altos`.
   * Configurar para: `Windows 10`.

### 2. Definir o Horário (Disparadores)
1. Vá na aba **Disparadores** > **Novo**.
2. Defina o horário que deseja que o robô acorde (ex: `08:00`).
3. Repetir tarefa a cada: `1 hora` (Opcional, se quiser garantir vários envios ao dia).

### 3. Configurar a Ação (O Segredo) ⚠️
Vá na aba **Ações** > **Novo** > **Iniciar um programa**. Preencha os campos exatamente assim:

* **Programa/Script:** Caminho do seu Python (use `pythonw.exe` para não abrir tela preta).
    * *Exemplo:* `C:\Users\SEU_USUARIO\AppData\Local\Programs\Python\Python312\pythonw.exe`
* **Adicione argumentos:**
    * `email_auto.py --robo`
* **Iniciar em (OBRIGATÓRIO):** O caminho da pasta onde está o arquivo `.py`.
    * *Exemplo:* `C:\email_automatico`

> **Nota:** Se o campo "Iniciar em" estiver vazio, o robô não achará o banco de dados e falhará silenciosamente.

---

## 📊 Modelo de Importação (Excel)

Para importar dados em massa, crie um arquivo Excel (`.xlsx`) com as seguintes colunas obrigatórias (nesta ordem ou com estes nomes de cabeçalho):

| Coluna | Descrição | Exemplo |
| :--- | :--- | :--- |
| **remetente** | Seu e-mail | `voce@empresa.com.br` |
| **senha** | Sua senha (será criptografada ao importar) | `SuaSenha123` |
| **destinatario** | E-mail do cliente | `cliente@gmail.com` |
| **assunto** | Assunto do e-mail | `Boleto Mensal` |
| **mensagem** | Corpo do e-mail | `Segue em anexo...` |
| **frequencia** | Tipo de envio | `Mensal`, `Unico`, `Semanal` |
| **dia** | Dia do mês (1-31) | `10` |
| **mes** | Mês (1-12) - *Para Anual/Único* | `5` |
| **ano** | Ano (yyyy) - *Para Único* | `2025` |
| **dia_semana** | 0=Seg, 1=Ter, ... 6=Dom - *Para Semanal* | `0` |

---

## 🔒 Segurança e Arquivos

* **`emails_auto.db`:** Banco de dados SQLite onde ficam os agendamentos e histórico.
* **`secret.key`:** Arquivo gerado automaticamente na primeira execução. **NUNCA APAGUE ESTE ARQUIVO.** Ele é a chave para descriptografar suas senhas. Se apagado, as senhas salvas serão perdidas.

---

## 🖥️ Como Usar (Interface)

1.  Execute `python email_auto.py` para abrir a interface.
2.  **Novo Agendamento:** Preencha os dados e escolha a frequência.
3.  **Lista:** Veja, edite ou exclua agendamentos. Use o botão 🚀 para forçar um envio imediato.
4.  **Histórico:** Acompanhe os logs de execução do robô (Sucesso em Verde / Erro em Vermelho).

---

## 🐞 Solução de Problemas Comuns

* **O histórico não atualiza:** Verifique se o campo "Iniciar em" no Agendador de Tarefas está preenchido corretamente.
* **Erro de Senha/Login:** Se trocou a senha do e-mail, edite o agendamento no sistema e salve novamente para atualizar a criptografia.
* **Tela preta abrindo:** Certifique-se de estar usando `pythonw.exe` e não `python.exe` no Agendador.

---

**Desenvolvido por:** Pedro H.G.C. Vidal
