import customtkinter as ctk

# --- CONFIGURAÇÕES VISUAIS ---
ctk.set_appearance_mode("Dark")        # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")    # Temas: "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuração da Janela
        self.title("Robô de E-mails - Design Preview")
        self.geometry("900x600")
        self.resizable(False, False) # Impede redimensionar para não quebrar o design

        # Layout Principal (Grid 1x2)
        # Coluna 0 = Menu Lateral (pequena)
        # Coluna 1 = Área de Conteúdo (grande)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === ESQUERDA: MENU LATERAL ===
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nswe")
        
        # Título do Menu
        self.lbl_logo = ctk.CTkLabel(self.frame_menu, text="AUTOMATOR\nE-MAILS", 
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(40, 30))

        # Botões do Menu
        self.btn_novo = ctk.CTkButton(self.frame_menu, text=" +  Novo Agendamento", 
                                      height=40, corner_radius=10,
                                      fg_color="transparent", border_width=2, 
                                      text_color=("gray10", "gray90"))
        self.btn_novo.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_lista = ctk.CTkButton(self.frame_menu, text=" ☰  Ver Lista", 
                                       height=40, corner_radius=10,
                                       fg_color="transparent", border_width=2, 
                                       text_color=("gray10", "gray90"))
        self.btn_lista.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # === DIREITA: ÁREA DE ABAS ===
        self.tabview = ctk.CTkTabview(self, width=650)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Criando as abas
        self.tab_cadastro = self.tabview.add("Cadastro")
        self.tab_visualizacao = self.tabview.add("Agendamentos")
        
        # Chamando as funções que desenham o conteúdo de cada aba
        self.desenhar_formulario()
        self.desenhar_lista_fake()

    def desenhar_formulario(self):
        """Desenha os campos na aba de Cadastro"""
        frame = ctk.CTkScrollableFrame(self.tab_cadastro, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        # Título da seção
        ctk.CTkLabel(frame, text="Configurar Novo Disparo", font=("Arial", 18, "bold")).pack(pady=(10, 20), anchor="w")

        # Campos (Labels + Entrys)
        self.criar_campo(frame, "E-mail Remetente (Locaweb):", "ex: pedro@mediphacos.com.br")
        self.criar_campo(frame, "Senha do E-mail:", "Digite sua senha...", senha=True)
        self.criar_campo(frame, "E-mail do Destinatário:", "ex: cliente@gmail.com")
        
        # Linha dupla (Dia e Assunto)
        frame_linha = ctk.CTkFrame(frame, fg_color="transparent")
        frame_linha.pack(fill="x", pady=5)
        
        # Dia (Pequeno)
        lbl_dia = ctk.CTkLabel(frame_linha, text="Dia (1-31):", font=("Arial", 12, "bold"))
        lbl_dia.pack(side="left")
        entry_dia = ctk.CTkEntry(frame_linha, width=60, placeholder_text="20")
        entry_dia.pack(side="left", padx=(10, 20))

        # Assunto (Grande)
        lbl_ass = ctk.CTkLabel(frame_linha, text="Assunto:", font=("Arial", 12, "bold"))
        lbl_ass.pack(side="left")
        entry_ass = ctk.CTkEntry(frame_linha, width=300, placeholder_text="Assunto do e-mail")
        entry_ass.pack(side="left", padx=10, fill="x", expand=True)

        # Campo de Mensagem (Grande)
        ctk.CTkLabel(frame, text="Mensagem / Corpo do E-mail:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        textbox = ctk.CTkTextbox(frame, height=150)
        textbox.pack(fill="x", pady=5)
        textbox.insert("0.0", "Olá,\n\nSegue conforme combinado...\n\nAtt,\nPedro")

        # Botão de Ação (Visual apenas)
        btn_salvar = ctk.CTkButton(frame, text="SALVAR AGENDAMENTO", 
                                   height=50, fg_color="#00a86b", 
                                   font=("Arial", 14, "bold"))
        btn_salvar.pack(pady=30, fill="x")

    def criar_campo(self, parent, titulo, placeholder, senha=False):
        """Função auxiliar para criar label + input repetidamente"""
        ctk.CTkLabel(parent, text=titulo, font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, show="*" if senha else "")
        entry.pack(fill="x", pady=(0, 10))

    def desenhar_lista_fake(self):
        """Desenha uma lista de exemplo para ver como vai ficar"""
        ctk.CTkLabel(self.tab_visualizacao, text="Envios Programados (Exemplo Visual)", font=("Arial", 16)).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(self.tab_visualizacao)
        scroll.pack(fill="both", expand=True)

        # Criando cards falsos
        for i in range(1, 6):
            card = ctk.CTkFrame(scroll, fg_color="#2b2b2b", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)
            
            # Texto do Card
            info = f"Destino: cliente_{i}@gmail.com  |  Dia: 20  |  Status: Ativo"
            ctk.CTkLabel(card, text=info, anchor="w").pack(side="left", padx=15, pady=15)
            
            # Botão Excluir
            ctk.CTkButton(card, text="✖", width=40, fg_color="#cf352e").pack(side="right", padx=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()