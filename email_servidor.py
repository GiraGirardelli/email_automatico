import sys
import sqlite3
import smtplib
import mimetypes
import os
import getpass  # <--- Para pegar o nome do usuário
from email.message import EmailMessage
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
from cryptography.fernet import Fernet 

# ============================================================================
# CONFIGURAÇÕES DE REDE 
# ============================================================================
# Aqui definimos que o banco vive no Drive S:
# O script verifica: Se o S: existir, usa ele. Se não, cria uma pasta local (fallback).

##NOME_PASTA_SERVIDOR = r"S:\Automacao_email" ## Place holder

##if os.path.exists("S:\\"):
##    PASTA_FINAL = NOME_PASTA_SERVIDOR
##else:
    # Se não achar o drive S cria local
# Define a pasta SERVER_FAKE dentro do projeto atual
PASTA_FINAL = os.path.join(os.getcwd(), "SERVER_FAKE")

# Tenta criar a pasta. Se der erro, o programa vai parar e te avisar (sem fallback)
if not os.path.exists(PASTA_FINAL):
    os.makedirs(PASTA_FINAL)
    print(f"✅ Pasta 'SERVER_FAKE' criada com sucesso em: {PASTA_FINAL}")
else:
    print(f"ℹ️ Usando pasta existente: {PASTA_FINAL}")

# Define os caminhos dos arquivos DENTRO da pasta
DB_NAME = os.path.join(PASTA_FINAL, "emails_central.db")
KEY_FILE = os.path.join(PASTA_FINAL, "chave_mestra.key")

print(f"📂 Banco de dados será salvo em: {DB_NAME}")

# ============================================================================
# PARTE 0: SEGURANÇA
# ============================================================================

def carregar_ou_criar_chave():
    if not os.path.exists(KEY_FILE):
        chave = Fernet.generate_key()
        with open(KEY_FILE, "wb") as k:
            k.write(chave)
    return open(KEY_FILE, "rb").read()

try:
    cipher = Fernet(carregar_ou_criar_chave())
except Exception as e:
    # Se der erro de permissão na rede avisa
    print(f"Erro de acesso à chave de segurança: {e}")
    sys.exit()

def criptografar(texto):
    if not texto: return ""
    return cipher.encrypt(texto.encode()).decode()

def descriptografar(texto_cripto):
    if not texto_cripto: return ""
    try:
        return cipher.decrypt(texto_cripto.encode()).decode()
    except:
        return texto_cripto

# ============================================================================
# PARTE 1: CÉREBRO 
# ============================================================================

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Cria a tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remetente TEXT,
            senha TEXT,
            destinatario TEXT,
            assunto TEXT,
            mensagem TEXT,
            frequencia TEXT,
            dia INTEGER,
            mes INTEGER,
            ano INTEGER,
            dia_semana INTEGER,
            anexo TEXT,
            dono TEXT  -- <--- Coluna do Dono
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            destinatario TEXT,
            status TEXT,
            detalhes TEXT
        )
    ''')
    
    # Migrações (Garante que colunas novas existam em bancos velhos)
    colunas_novas = [
        ("anexo", "TEXT"), 
        ("frequencia", "TEXT"), ("dia", "INTEGER"), 
        ("mes", "INTEGER"), ("ano", "INTEGER"), 
        ("dia_semana", "INTEGER"), ("dono", "TEXT")
    ]
    for col, tipo in colunas_novas:
        try: cursor.execute(f"ALTER TABLE agendamentos ADD COLUMN {col} {tipo}")
        except: pass

    # Ativa modo WAL ( para acesso simultâneo em rede)
    cursor.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    conn.close()

def registrar_log(destinatario, status, detalhes):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico (data_hora, destinatario, status, detalhes) VALUES (?, ?, ?, ?)",
                       (data_hora, destinatario, status, detalhes))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao gravar log: {e}")

def enviar_email(remetente, senha_cripto, destinatario, assunto, corpo, caminho_anexo=None, manual=False):
    senha_real = descriptografar(senha_cripto)
    
    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destinatario
    msg.set_content(corpo)

    # Verifica anexo (tenta achar no caminho original, se falhar avisa)
    if caminho_anexo and os.path.exists(caminho_anexo):
        try:
            mime_type, _ = mimetypes.guess_type(caminho_anexo)
            if mime_type is None: mime_type = 'application/octet-stream'
            maintype, subtype = mime_type.split('/', 1)
            with open(caminho_anexo, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(caminho_anexo)
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
        except Exception as e:
            print(f"Erro ao anexar: {e}")
            
    try:
        with smtplib.SMTP_SSL('email-ssl.com.br', 465) as smtp:
            smtp.login(remetente, senha_real)
            smtp.send_message(msg)
        
        tipo = "[MANUAL]" if manual else "[AUTO]"
        registrar_log(destinatario, "SUCESSO", f"{tipo} E-mail enviado.")
        return True
    except Exception as e:
        registrar_log(destinatario, "ERRO", str(e))
        return False

def verificar_rotina_automatica():
    agora = datetime.now()
    # Verifica dia, mes, ano e semana...
    
    print(f"--- Robô Iniciado no Servidor: {agora} ---")
    print(f"--- Lendo Banco: {DB_NAME} ---")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agendamentos")
        tarefas = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar no banco do servidor: {e}")
        return

    if not tarefas: return
    
    for tarefa in tarefas:
        try:
            # Desempacota considerando a nova coluna 'dono'
            if len(tarefa) == 13:
                id_bd, reme, senha, dest, ass, msg, freq, dia, mes, ano, d_sem, anexo, dono = tarefa
            else:
                # Compatibilidade com versões antigas
                id_bd, reme, senha, dest, ass, msg, freq, dia, mes, ano, d_sem, anexo = tarefa
                dono = "LEGADO"
        except: continue

        enviar = False
        # (Lógica de datas) 
        dia_hoje = agora.day
        mes_hoje = agora.month
        ano_hoje = agora.year
        semana_hoje = agora.weekday()

        if freq == "Diario": enviar = True
        elif freq == "Semanal" and d_sem == semana_hoje: enviar = True
        elif freq == "Mensal" and dia == dia_hoje: enviar = True
        elif freq == "Anual" and dia == dia_hoje and mes == mes_hoje: enviar = True
        elif freq == "Unico" and dia == dia_hoje and mes == mes_hoje and ano == ano_hoje: enviar = True

        if enviar:
            print(f"Processando tarefa de: {dono}")
            sucesso = enviar_email(reme, senha, dest, ass, msg, anexo, manual=False)
            if sucesso and freq == "Unico":
                conn_del = sqlite3.connect(DB_NAME)
                conn_del.execute("DELETE FROM agendamentos WHERE id = ?", (id_bd,))
                conn_del.commit()
                conn_del.close()

# ============================================================================
# PARTE 2: Interface
# ============================================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de E-mail Corporativo - (Versão Servidor)")
        self.geometry("1100x750")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.usuario_atual = getpass.getuser().upper() # PEGA NOME DO USUÁRIO
        
        self.id_em_edicao = None
        self.caminho_anexo_selecionado = None
        
        self.setup_layout_principal()

    def setup_layout_principal(self):
        # Menu Lateral
        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nswe")
        
        ctk.CTkLabel(self.menu_frame, text="MENU CORP", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkLabel(self.menu_frame, text=f"Olá, {self.usuario_atual}", text_color="cyan").grid(row=1, column=0)
        
        self.btn_novo = ctk.CTkButton(self.menu_frame, text="Novo Agendamento", command=lambda: self.tabview.set("Novo"))
        self.btn_novo.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_lista = ctk.CTkButton(self.menu_frame, text="Todos Agendamentos", fg_color="transparent", border_width=2, command=self.mostrar_aba_lista)
        self.btn_lista.grid(row=3, column=0, padx=20, pady=10)

        self.btn_hist = ctk.CTkButton(self.menu_frame, text="Logs do Servidor", fg_color="transparent", border_width=2, command=self.mostrar_aba_hist)
        self.btn_hist.grid(row=4, column=0, padx=20, pady=10)
        
        # Caminho do Banco (Rodapé)
        ctk.CTkLabel(self.menu_frame, text="Conectado em:", font=("Arial", 10)).grid(row=9, column=0, pady=(50,0))
        ctk.CTkLabel(self.menu_frame, text=DB_NAME, font=("Arial", 9), text_color="gray", wraplength=180).grid(row=10, column=0)

        # Abas
        self.tabview = ctk.CTkTabview(self, width=650)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tab_novo = self.tabview.add("Novo")
        self.tab_lista = self.tabview.add("Lista")
        self.tab_hist = self.tabview.add("Histórico")
        self.tabview._segmented_button.grid_forget() 
        
        self.setup_form()
        self.setup_lista()
        self.setup_historico()

    def setup_form(self):
        frame = ctk.CTkScrollableFrame(self.tab_novo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        self.btn_cancelar = ctk.CTkButton(header, text="Cancelar Edição", fg_color="gray", command=self.limpar_campos)
        ctk.CTkButton(header, text="📊 Importar Excel", fg_color="#207245", command=self.importar_excel).pack(side="right")

        self.criar_input(frame, "Seu E-mail:", "reme")
        self.criar_input(frame, "Sua Senha:", "sen", senha=True)
        self.criar_input(frame, "Destinatário:", "dest")
        
        ctk.CTkLabel(frame, text="Quando enviar?", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.cmb_freq = ctk.CTkComboBox(frame, values=["Diario", "Semanal", "Mensal", "Anual", "Unico"], command=self.atualizar_inputs_freq)
        self.cmb_freq.pack(anchor="w", pady=(0, 10))
        self.cmb_freq.set("Mensal")

        self.frame_datas = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_datas.pack(fill="x", pady=5)
        
        self.inputs_data = {}
        self.inputs_data['lbl_dia'] = ctk.CTkLabel(self.frame_datas, text="Dia:", width=40)
        self.inputs_data['ent_dia'] = ctk.CTkEntry(self.frame_datas, width=60)
        self.inputs_data['lbl_mes'] = ctk.CTkLabel(self.frame_datas, text="Mês:", width=40)
        self.inputs_data['ent_mes'] = ctk.CTkEntry(self.frame_datas, width=60)
        self.inputs_data['lbl_ano'] = ctk.CTkLabel(self.frame_datas, text="Ano:", width=50)
        self.inputs_data['ent_ano'] = ctk.CTkEntry(self.frame_datas, width=80)
        self.inputs_data['lbl_sem'] = ctk.CTkLabel(self.frame_datas, text="Dia da Semana:")
        self.inputs_data['cmb_sem'] = ctk.CTkComboBox(self.frame_datas, values=["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"])
        self.atualizar_inputs_freq("Mensal")

        self.criar_input(frame, "Assunto:", "ass")
        ctk.CTkLabel(frame, text="Mensagem:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.txt_msg = ctk.CTkTextbox(frame, height=150)
        self.txt_msg.pack(fill="x", pady=(0, 10))

        self.lbl_anexo = ctk.CTkLabel(frame, text="Nenhum arquivo selecionado", text_color="gray")
        self.lbl_anexo.pack(pady=(5, 0))
        ctk.CTkButton(frame, text="📎 Anexar Arquivo", fg_color="#555", command=self.selecionar_arquivo).pack(pady=(0, 10))

        self.btn_salvar = ctk.CTkButton(frame, text="SALVAR NO SERVIDOR", fg_color="green", height=40, command=self.salvar)
        self.btn_salvar.pack(pady=20)

    def criar_input(self, parent, texto, attr_name, senha=False):
        ctk.CTkLabel(parent, text=texto, font=("Arial", 12, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(parent, show="*" if senha else "", width=400)
        entry.pack(anchor="w", pady=(0, 10), fill="x")
        setattr(self, f"entry_{attr_name}", entry)

    def atualizar_inputs_freq(self, escolha=None):
        for w in self.frame_datas.winfo_children(): w.pack_forget()
        freq = self.cmb_freq.get()
        if freq == "Diario":
            ctk.CTkLabel(self.frame_datas, text="Envio diário automático.", text_color="gray").pack(anchor="w")
        elif freq == "Semanal":
            self.inputs_data['lbl_sem'].pack(side="left", padx=5)
            self.inputs_data['cmb_sem'].pack(side="left")
        elif freq == "Mensal":
            self.inputs_data['lbl_dia'].pack(side="left", padx=5)
            self.inputs_data['ent_dia'].pack(side="left")
        elif freq == "Anual":
            self.inputs_data['lbl_dia'].pack(side="left", padx=5)
            self.inputs_data['ent_dia'].pack(side="left")
            self.inputs_data['lbl_mes'].pack(side="left", padx=5)
            self.inputs_data['ent_mes'].pack(side="left")
        elif freq == "Unico":
            self.inputs_data['lbl_dia'].pack(side="left", padx=5)
            self.inputs_data['ent_dia'].pack(side="left")
            self.inputs_data['lbl_mes'].pack(side="left", padx=5)
            self.inputs_data['ent_mes'].pack(side="left")
            self.inputs_data['lbl_ano'].pack(side="left", padx=5)
            self.inputs_data['ent_ano'].pack(side="left")

    def salvar(self):
        freq = self.cmb_freq.get()
        dia, mes, ano, d_sem = 0, 0, 0, 0
        try:
            if freq == "Semanal":
                dias_map = {"Segunda":0, "Terca":1, "Quarta":2, "Quinta":3, "Sexta":4, "Sabado":5, "Domingo":6}
                d_sem = dias_map[self.inputs_data['cmb_sem'].get()]
            if freq in ["Mensal", "Anual", "Unico"]:
                dia = int(self.inputs_data['ent_dia'].get())
                if not (1 <= dia <= 31): raise ValueError("Dia inválido")
            if freq in ["Anual", "Unico"]:
                mes = int(self.inputs_data['ent_mes'].get())
                if not (1 <= mes <= 12): raise ValueError("Mês inválido")
            if freq == "Unico":
                ano = int(self.inputs_data['ent_ano'].get())
                if ano < 2024: raise ValueError("Ano inválido")
        except ValueError as e:
            messagebox.showerror("Erro de Data", str(e))
            return

        senha_pura = self.entry_sen.get()
        senha_segura = criptografar(senha_pura)

        dados = [
            self.entry_reme.get(), senha_segura,
            self.entry_dest.get(), self.entry_ass.get(), 
            self.txt_msg.get("1.0", "end-1c"), 
            freq, dia, mes, ano, d_sem,
            self.caminho_anexo_selecionado,
            self.usuario_atual # <--- SALVA O NOME DO USUÁRIO
        ]

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            if self.id_em_edicao:
                dados.append(self.id_em_edicao)
                cursor.execute("""
                    UPDATE agendamentos 
                    SET remetente=?, senha=?, destinatario=?, assunto=?, mensagem=?, 
                        frequencia=?, dia=?, mes=?, ano=?, dia_semana=?, anexo=?, dono=?
                    WHERE id=?
                """, dados)
                msg_sucesso = "Atualizado no Servidor!"
            else:
                cursor.execute("""
                    INSERT INTO agendamentos 
                    (remetente, senha, destinatario, assunto, mensagem, frequencia, dia, mes, ano, dia_semana, anexo, dono)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, dados)
                msg_sucesso = "Salvo no Servidor!"
                
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", msg_sucesso)
            self.limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro de Rede", f"Não foi possível salvar no S:\n{e}")

    def importar_excel(self):
        messagebox.showinfo("Aviso", "O Excel deve ter colunas: remetente, senha, destinatario, assunto, mensagem, frequencia, dia, mes, ano, dia_semana")
        caminho = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not caminho: return
        try:
            df = pd.read_excel(caminho)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cont = 0
            for index, row in df.iterrows():
                senha_segura = criptografar(str(row['senha']))
                dia = row['dia'] if pd.notna(row['dia']) else 0
                mes = row['mes'] if pd.notna(row['mes']) else 0
                ano = row['ano'] if pd.notna(row['ano']) else 0
                d_sem = row['dia_semana'] if pd.notna(row['dia_semana']) else 0

                cursor.execute("""
                    INSERT INTO agendamentos (remetente, senha, destinatario, assunto, mensagem, frequencia, dia, mes, ano, dia_semana, dono)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (row['remetente'], senha_segura, row['destinatario'], row['assunto'], row['mensagem'], row['frequencia'], dia, mes, ano, d_sem, self.usuario_atual))
                cont += 1
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", f"{cont} importados para o servidor!")
            self.mostrar_aba_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Detalhe: {e}")

    def carregar_dados(self):
        for widget in self.frame_lista.winfo_children(): widget.destroy()
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agendamentos")
            items = cursor.fetchall()
            conn.close()
        except:
            ctk.CTkLabel(self.frame_lista, text="Erro ao conectar no banco S:").pack()
            return

        if not items:
            ctk.CTkLabel(self.frame_lista, text="Nenhum agendamento no servidor.").pack(pady=20)
            return

        for item in items:
            try:
                # Tenta desempacotar com DONO
                if len(item) == 13:
                    id_bd, _, _, dest, ass, _, freq, dia, mes, ano, d_sem, anexo, dono = item
                else:
                    id_bd, _, _, dest, ass, _, freq, dia, mes, ano, d_sem, anexo = item
                    dono = "Desconhecido"
            except: continue
            
            card = ctk.CTkFrame(self.frame_lista, fg_color="#2b2b2b")
            card.pack(fill="x", pady=5, padx=5)
            
            txt_data = freq
            if freq == "Semanal":
                dias_rev = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
                txt_data = f"Semanal ({dias_rev[d_sem]})"
            elif freq == "Mensal": txt_data = f"Todo dia {dia}"
            elif freq == "Anual": txt_data = f"Anual ({dia}/{mes})"
            elif freq == "Unico": txt_data = f"Único ({dia}/{mes}/{ano})"
            
            info = f"{txt_data} | Para: {dest}\nAssunto: {ass}"
            ctk.CTkLabel(card, text=info, anchor="w", justify="left").pack(side="left", padx=10, pady=10)
            
            # MOSTRA O DONO NO CANTO
            ctk.CTkLabel(card, text=f"👤 {dono}", font=("Arial", 10, "bold"), text_color="#aaa").pack(side="right", padx=10)
            
            ctk.CTkButton(card, text="✖", fg_color="#cf352e", width=40, command=lambda i=id_bd: self.excluir_item(i)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="✎", fg_color="#d97b00", width=40, command=lambda dados=item: self.preparar_edicao(dados)).pack(side="right", padx=5)
            
    def preparar_edicao(self, dados):
        # ... (Mantém lógica de preenchimento, adaptando se tiver dono no final)
        self.id_em_edicao = dados[0]
        self.limpar_campos(reset_mode=False) 
        
        self.entry_reme.insert(0, dados[1])
        senha_real = descriptografar(dados[2])
        self.entry_sen.insert(0, senha_real)
        self.entry_dest.insert(0, dados[3])
        self.entry_ass.insert(0, dados[4])
        self.txt_msg.insert("0.0", dados[5])
        
        freq, dia, mes, ano, d_sem = dados[6], dados[7], dados[8], dados[9], dados[10]
        self.cmb_freq.set(freq)
        self.atualizar_inputs_freq()
        
        # (Resto do preenchimento)
        if freq == "Semanal":
            dias_rev = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
            try: self.inputs_data['cmb_sem'].set(dias_rev[d_sem])
            except: pass
        if dia: self.inputs_data['ent_dia'].insert(0, str(dia))
        if mes: self.inputs_data['ent_mes'].insert(0, str(mes))
        if ano: self.inputs_data['ent_ano'].insert(0, str(ano))

        self.caminho_anexo_selecionado = dados[11]
        if self.caminho_anexo_selecionado:
            self.lbl_anexo.configure(text=f"📎 {os.path.basename(self.caminho_anexo_selecionado)}", text_color="cyan")

        self.btn_salvar.configure(text="ATUALIZAR (S:)", fg_color="#d97b00")
        self.btn_cancelar.pack(side="left", padx=10)
        self.tabview.set("Novo")

    # (Resto das funções auxiliares)
    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename()
        if caminho:
            self.caminho_anexo_selecionado = caminho
            self.lbl_anexo.configure(text=f"📎 {os.path.basename(caminho)}", text_color="cyan")

    def limpar_campos(self, reset_mode=True):
        self.entry_dest.delete(0, "end")
        self.entry_ass.delete(0, "end")
        self.txt_msg.delete("0.0", "end")
        self.inputs_data['ent_dia'].delete(0, "end")
        self.inputs_data['ent_mes'].delete(0, "end")
        self.inputs_data['ent_ano'].delete(0, "end")
        self.caminho_anexo_selecionado = None
        self.lbl_anexo.configure(text="Nenhum arquivo", text_color="gray")
        if reset_mode:
            self.id_em_edicao = None
            self.btn_salvar.configure(text="SALVAR NO SERVIDOR", fg_color="green")
            self.btn_cancelar.pack_forget()
            self.mostrar_aba_lista()

    def excluir_item(self, id_item):
        if not messagebox.askyesno("Confirmar", "Excluir do Servidor?"): return
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM agendamentos WHERE id = ?", (id_item,))
        conn.commit()
        conn.close()
        self.carregar_dados()

    def mostrar_aba_lista(self): 
        self.tabview.set("Lista")
        self.carregar_dados()
    def mostrar_aba_hist(self):
        self.tabview.set("Histórico")
        self.carregar_historico()

    def setup_lista(self):
        self.frame_lista = ctk.CTkScrollableFrame(self.tab_lista)
        self.frame_lista.pack(fill="both", expand=True)
        ctk.CTkButton(self.tab_lista, text="Atualizar Lista (S:)", command=self.carregar_dados).pack(pady=10)

    def setup_historico(self):
        self.frame_hist = ctk.CTkScrollableFrame(self.tab_hist)
        self.frame_hist.pack(fill="both", expand=True)
        ctk.CTkButton(self.tab_hist, text="Atualizar Logs", command=self.carregar_historico).pack(pady=5)

    def carregar_historico(self):
        for w in self.frame_hist.winfo_children(): w.destroy()
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT data_hora, destinatario, status, detalhes FROM historico ORDER BY id DESC LIMIT 20")
            logs = cursor.fetchall()
            conn.close()
        except:
            return

        for log in logs:
            data, dest, status, detalhe = log
            cor_texto = "#2cc985" if "SUCESSO" in status.upper() else "#ff4d4d"
            cor_borda = "#2cc985" if "SUCESSO" in status.upper() else "#cf352e"
            
            card = ctk.CTkFrame(self.frame_hist, fg_color="#2b2b2b", border_width=2, border_color=cor_borda)
            card.pack(fill="x", pady=5, padx=5)
            
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5,0))
            ctk.CTkLabel(header, text=data, font=("Arial", 11), text_color="gray").pack(side="left")
            ctk.CTkLabel(header, text=status, font=("Arial", 12, "bold"), text_color=cor_texto).pack(side="right")
            ctk.CTkLabel(card, text=f"Para: {dest}", font=("Arial", 14, "bold"), anchor="w").pack(fill="x", padx=10, pady=(5,0))
            ctk.CTkLabel(card, text=detalhe, font=("Arial", 12), text_color="#dce4ee", anchor="w", justify="left", wraplength=400).pack(fill="x", padx=10, pady=(0,10))

if __name__ == "__main__":
    inicializar_db()
    if len(sys.argv) > 1 and sys.argv[1] == "--robo":
        verificar_rotina_automatica()
    else:
        app = App()
        app.mainloop()