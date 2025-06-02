import tkinter as tk
from tkinter import ttk, messagebox, font
import datetime
import os
import sys
import re

# Tente importar o gerenciador de tarefas
try:
    from commands.gerenciador_tarefas import GerenciadorTarefas
except ImportError:
    print("Erro ao importar GerenciadorTarefas. Verifique se o arquivo está no caminho correto.")
    sys.exit(1)

class AssistenteGUIModerno:
    def __init__(self):
        # Inicializar janela principal primeiro
        self.root = tk.Tk()
        self.root.title("Assistente Virtual - Gerenciador de Tarefas")
        self.root.geometry("900x650")
        
        # Definir cores e estilos
        self.definir_estilos()
        
        # Inicializar variáveis de estado
        self.tarefas = []
        
        # Criar status bar primeiro para evitar o erro
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, style="StatusBar.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Inicializar gerenciador
        try:
            self.gerenciador = GerenciadorTarefas()
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", f"Erro ao inicializar o gerenciador de tarefas: {str(e)}")
            self.root.destroy()
            return
        
        # Criar cabeçalho
        self.criar_cabecalho()
        
        # Criar notebook (abas)
        self.criar_notebook()
        
        # Configurar cada aba
        self.configurar_aba_assistente()
        self.configurar_aba_tarefas()
        self.configurar_aba_calendario()
        
        # Carregar tarefas iniciais
        try:
            self.carregar_tarefas()
        except Exception as e:
            # Apenas registrar o erro, não interromper a inicialização
            print(f"Erro ao carregar tarefas iniciais: {str(e)}")
            self.atualizar_status("Erro ao carregar tarefas iniciais")
    
    def definir_estilos(self):
        """Define estilos e cores para a interface"""
        # Cores
        self.cor_primaria = "#3498db"  # Azul
        self.cor_secundaria = "#2ecc71"  # Verde
        self.cor_destaque = "#e74c3c"  # Vermelho
        self.cor_fundo = "#f5f5f5"  # Cinza claro
        self.cor_texto = "#2c3e50"  # Azul escuro
        self.cor_texto_claro = "#ecf0f1"  # Branco acinzentado
        
        # Configurar tema da janela
        self.root.configure(bg=self.cor_fundo)
        
        # Criar estilos para ttk
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.cor_fundo)
        self.style.configure("TLabel", background=self.cor_fundo, foreground=self.cor_texto)
        self.style.configure("TButton", background=self.cor_primaria, foreground=self.cor_texto)
        self.style.configure("TNotebook", background=self.cor_fundo)
        self.style.configure("TNotebook.Tab", background=self.cor_fundo, foreground=self.cor_texto, padding=[10, 5])
        self.style.map("TNotebook.Tab", 
                       background=[("selected", self.cor_primaria)],
                       foreground=[("selected", self.cor_texto_claro)])
        
        # Estilo para barra de status
        self.style.configure("StatusBar.TLabel", background="#f0f0f0", foreground=self.cor_texto)
        
        # Estilo para botões de ação
        self.style.configure("Action.TButton", background=self.cor_primaria, foreground=self.cor_texto)
        self.style.map("Action.TButton",
                      background=[("active", self.cor_secundaria)],
                      foreground=[("active", self.cor_texto)])
        
        # Estilo para botões de perigo
        self.style.configure("Danger.TButton", background=self.cor_destaque, foreground=self.cor_texto)
        self.style.map("Danger.TButton",
                      background=[("active", "#c0392b")],  # Vermelho mais escuro
                      foreground=[("active", self.cor_texto)])
        
        # Estilo para botões secundários
        self.style.configure("Secondary.TButton", background="#95a5a6", foreground=self.cor_texto)
        self.style.map("Secondary.TButton",
                      background=[("active", "#7f8c8d")],
                      foreground=[("active", self.cor_texto)])
        
        # Estilo para cabeçalhos
        self.style.configure("Header.TLabel", background=self.cor_primaria, foreground=self.cor_texto_claro, font=("Arial", 14, "bold"))
        
        # Estilo para títulos
        self.style.configure("Title.TLabel", background=self.cor_fundo, foreground=self.cor_texto, font=("Arial", 14, "bold"))
        
        # Estilo para subtítulos
        self.style.configure("Subtitle.TLabel", background=self.cor_fundo, foreground=self.cor_texto, font=("Arial", 12, "bold"))
        
        # Estilo para frames de conteúdo
        self.style.configure("Content.TFrame", background=self.cor_fundo)
        
        # Estilo para frames de destaque
        self.style.configure("Highlight.TFrame", background="#e0e0e0")
    
    def criar_cabecalho(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill=tk.X)
        
        # Logo/Título
        logo_label = ttk.Label(
            header_frame, 
            text="Assistente Virtual",
            style="Header.TLabel",
            padding=(10, 5)
        )
        logo_label.pack(side=tk.LEFT)
        
        # Versão
        version_label = ttk.Label(
            header_frame,
            text="v1.0",
            style="Header.TLabel",
            padding=(5, 5)
        )
        version_label.pack(side=tk.RIGHT)
    
    def criar_notebook(self):
        """Cria o notebook (sistema de abas)"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar frames para cada aba
        self.frame_assistente = ttk.Frame(self.notebook, style="Content.TFrame")
        self.frame_tarefas = ttk.Frame(self.notebook, style="Content.TFrame")
        self.frame_calendario = ttk.Frame(self.notebook, style="Content.TFrame")
        
        # Adicionar abas ao notebook
        self.notebook.add(self.frame_assistente, text="Assistente")
        self.notebook.add(self.frame_tarefas, text="Tarefas")
        self.notebook.add(self.frame_calendario, text="Calendário")
        
        # Vincular evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Manipula o evento de mudança de aba"""
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Calendário":
            # Atualizar eventos do dia ao mudar para a aba de calendário
            self.atualizar_eventos_dia()
        elif tab_name == "Tarefas":
            # Atualizar lista de tarefas ao mudar para a aba de tarefas
            self.carregar_tarefas()
    
    def configurar_aba_assistente(self):
        """Configura a aba principal do assistente"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.frame_assistente, style="Content.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="Assistente Virtual de Tarefas", 
            style="Title.TLabel"
        )
        titulo.pack(pady=10)
        
        # Área de entrada
        input_frame = ttk.Frame(main_frame, style="Content.TFrame")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            input_frame, 
            text="Digite seu comando:",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        # Frame para entrada e botão
        entry_button_frame = ttk.Frame(input_frame, style="Content.TFrame")
        entry_button_frame.pack(fill=tk.X)
        
        self.entrada = ttk.Entry(
            entry_button_frame,
            font=("Arial", 11),
            width=50
        )
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entrada.bind("<Return>", lambda e: self.processar_comando())
        self.entrada.focus_set()
        
        ttk.Button(
            entry_button_frame,
            text="Executar",
            style="Action.TButton",
            command=self.processar_comando
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            entry_button_frame,
            text="Sugestões",
            style="Secondary.TButton",
            command=self.mostrar_sugestoes
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Exemplos de comandos
        examples_frame = ttk.LabelFrame(main_frame, text="Exemplos de comandos", padding=10)
        examples_frame.pack(fill=tk.X, pady=10)
        
        examples = [
            "Adicionar reunião com equipe amanhã às 14h",
            "Lembrar de enviar relatório na sexta-feira",
            "Listar tarefas da próxima semana",
            "Marcar consulta médica dia 10/06 às 9h"
        ]
        
        for example in examples:
            example_frame = ttk.Frame(examples_frame, style="Content.TFrame")
            example_frame.pack(fill=tk.X, pady=2)
            
            # Criar botão "Usar" com estilo personalizado para garantir contraste
            usar_btn = tk.Button(
                example_frame,
                text="Usar",
                width=6,
                bg="#3498db",  # Azul
                fg="#ffffff",  # Branco
                relief=tk.RAISED,
                command=lambda cmd=example: self.usar_exemplo(cmd)
            )
            usar_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(
                example_frame,
                text=example,
                wraplength=600
            ).pack(side=tk.LEFT, fill=tk.X)
        
        # Área de histórico
        history_frame = ttk.LabelFrame(main_frame, text="Histórico de comandos", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para o texto e scrollbar
        text_frame = ttk.Frame(history_frame, style="Content.TFrame")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.historico = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg="white",
            bd=1,
            relief=tk.SOLID,
            font=("Arial", 10),
            height=15
        )
        self.historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.historico.configure(state='disabled')
        
        # Configurar scrollbar
        self.historico.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.historico.yview)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame, style="Content.TFrame")
        action_frame.pack(fill=tk.X, pady=10)
        
        # Botão Limpar Histórico com estilo personalizado para garantir contraste
        limpar_btn = tk.Button(
            action_frame,
            text="Limpar Histórico",
            bg="#95a5a6",  # Cinza
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.limpar_historico
        )
        limpar_btn.pack(side=tk.RIGHT)
    
    def configurar_aba_tarefas(self):
        """Configura a aba de listagem e gerenciamento de tarefas"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.frame_tarefas, style="Content.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="Gerenciamento de Tarefas", 
            style="Title.TLabel"
        )
        titulo.pack(pady=10)
        
        # Filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Grid para filtros
        filter_grid = ttk.Frame(filter_frame, style="Content.TFrame")
        filter_grid.pack(fill=tk.X)
        
        # Categoria
        ttk.Label(filter_grid, text="Categoria:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        categorias = ["todas", "trabalho", "pessoal", "estudo", "geral"]
        self.categoria_var = tk.StringVar(value="todas")
        self.combo_categoria = ttk.Combobox(filter_grid, textvariable=self.categoria_var, values=categorias, state="readonly", width=15)
        self.combo_categoria.grid(row=0, column=1, padx=5, pady=5)
        
        # Prioridade
        ttk.Label(filter_grid, text="Prioridade:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        prioridades = ["todas", "alta", "média", "baixa", "normal"]
        self.prioridade_var = tk.StringVar(value="todas")
        self.combo_prioridade = ttk.Combobox(filter_grid, textvariable=self.prioridade_var, values=prioridades, state="readonly", width=15)
        self.combo_prioridade.grid(row=0, column=3, padx=5, pady=5)
        
        # Data
        ttk.Label(filter_grid, text="Data:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.data_filtro_var = tk.StringVar(value="")
        ttk.Entry(filter_grid, textvariable=self.data_filtro_var, width=12).grid(row=0, column=5, padx=5, pady=5)
        
        # Botões de filtro
        filter_buttons = ttk.Frame(filter_frame, style="Content.TFrame")
        filter_buttons.pack(fill=tk.X, pady=(10, 0))
        
        # Botões com estilo personalizado para garantir contraste
        aplicar_btn = tk.Button(
            filter_buttons,
            text="Aplicar Filtros",
            bg="#3498db",  # Azul
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.filtrar_tarefas
        )
        aplicar_btn.pack(side=tk.LEFT, padx=5)
        
        limpar_btn = tk.Button(
            filter_buttons,
            text="Limpar Filtros",
            bg="#95a5a6",  # Cinza
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.limpar_filtros
        )
        limpar_btn.pack(side=tk.LEFT, padx=5)
        
        atualizar_btn = tk.Button(
            filter_buttons,
            text="Atualizar Lista",
            bg="#2ecc71",  # Verde
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.carregar_tarefas
        )
        atualizar_btn.pack(side=tk.LEFT, padx=5)
        
        # Lista de tarefas (Treeview)
        list_frame = ttk.LabelFrame(main_frame, text="Lista de Tarefas", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para o treeview e scrollbar
        tree_frame = ttk.Frame(list_frame, style="Content.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tarefas_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "titulo", "data", "hora", "categoria", "prioridade"),
            show="headings",
            selectmode="browse"
        )
        self.tarefas_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        self.tarefas_tree.heading("id", text="ID")
        self.tarefas_tree.heading("titulo", text="Título")
        self.tarefas_tree.heading("data", text="Data")
        self.tarefas_tree.heading("hora", text="Hora")
        self.tarefas_tree.heading("categoria", text="Categoria")
        self.tarefas_tree.heading("prioridade", text="Prioridade")
        
        # Configurar larguras
        self.tarefas_tree.column("id", width=50, minwidth=50)
        self.tarefas_tree.column("titulo", width=250, minwidth=150)
        self.tarefas_tree.column("data", width=100, minwidth=100)
        self.tarefas_tree.column("hora", width=80, minwidth=80)
        self.tarefas_tree.column("categoria", width=100, minwidth=100)
        self.tarefas_tree.column("prioridade", width=100, minwidth=100)
        
        # Configurar scrollbar
        self.tarefas_tree.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tarefas_tree.yview)
        
        # Vincular evento de seleção
        self.tarefas_tree.bind("<<TreeviewSelect>>", self.mostrar_detalhes_tarefa)
        
        # Painel de detalhes
        details_frame = ttk.LabelFrame(main_frame, text="Detalhes da tarefa", padding=10)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Frame para o texto e scrollbar
        details_text_frame = ttk.Frame(details_frame, style="Content.TFrame")
        details_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        details_scrollbar = ttk.Scrollbar(details_text_frame)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.detalhes_tarefa = tk.Text(
            details_text_frame,
            wrap=tk.WORD,
            bg="white",
            bd=1,
            relief=tk.SOLID,
            font=("Arial", 10),
            height=5
        )
        self.detalhes_tarefa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.detalhes_tarefa.configure(state='disabled')
        
        # Configurar scrollbar
        self.detalhes_tarefa.config(yscrollcommand=details_scrollbar.set)
        details_scrollbar.config(command=self.detalhes_tarefa.yview)
        
        # Botões de ação
        actions_frame = ttk.Frame(main_frame, style="Content.TFrame")
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Botões com estilo personalizado para garantir contraste
        nova_btn = tk.Button(
            actions_frame,
            text="Nova Tarefa",
            bg="#3498db",  # Azul
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.nova_tarefa
        )
        nova_btn.pack(side=tk.LEFT, padx=5)
        
        editar_btn = tk.Button(
            actions_frame,
            text="Editar",
            bg="#f39c12",  # Laranja
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.editar_tarefa
        )
        editar_btn.pack(side=tk.LEFT, padx=5)
        
        excluir_btn = tk.Button(
            actions_frame,
            text="Excluir",
            bg="#e74c3c",  # Vermelho
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.excluir_tarefa
        )
        excluir_btn.pack(side=tk.LEFT, padx=5)
    
    def configurar_aba_calendario(self):
        """Configura a aba de visualização de calendário"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.frame_calendario, style="Content.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="Calendário de Tarefas", 
            style="Title.TLabel"
        )
        titulo.pack(pady=10)
        
        # Layout de duas colunas
        content_frame = ttk.Frame(main_frame, style="Content.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna esquerda - Calendário
        left_frame = ttk.Frame(content_frame, style="Content.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Controles de navegação
        nav_frame = ttk.Frame(left_frame, style="Content.TFrame")
        nav_frame.pack(fill=tk.X, pady=5)
        
        # Mês e ano
        month_year_frame = ttk.Frame(nav_frame, style="Content.TFrame")
        month_year_frame.pack(side=tk.LEFT)
        
        ttk.Label(month_year_frame, text="Mês:").pack(side=tk.LEFT, padx=5)
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.mes_var = tk.StringVar(value=meses[datetime.datetime.now().month - 1])
        self.combo_mes = ttk.Combobox(month_year_frame, textvariable=self.mes_var, values=meses, state="readonly", width=12)
        self.combo_mes.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(month_year_frame, text="Ano:").pack(side=tk.LEFT, padx=5)
        ano_atual = datetime.datetime.now().year
        anos = [str(y) for y in range(ano_atual - 2, ano_atual + 5)]
        self.ano_var = tk.StringVar(value=str(ano_atual))
        self.combo_ano = ttk.Combobox(month_year_frame, textvariable=self.ano_var, values=anos, state="readonly", width=6)
        self.combo_ano.pack(side=tk.LEFT, padx=5)
        
        # Botões de navegação
        nav_buttons = ttk.Frame(nav_frame, style="Content.TFrame")
        nav_buttons.pack(side=tk.RIGHT)
        
        # Botões com estilo personalizado para garantir contraste
        visualizar_btn = tk.Button(
            nav_buttons,
            text="Visualizar",
            bg="#3498db",  # Azul
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.atualizar_calendario
        )
        visualizar_btn.pack(side=tk.LEFT, padx=5)
        
        hoje_btn = tk.Button(
            nav_buttons,
            text="Hoje",
            bg="#2ecc71",  # Verde
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=self.ir_para_hoje
        )
        hoje_btn.pack(side=tk.LEFT, padx=5)
        
        # Calendário
        cal_frame = ttk.LabelFrame(left_frame, text="Calendário", padding=10)
        cal_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para o calendário
        self.cal_frame = ttk.Frame(cal_frame, style="Content.TFrame")
        self.cal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar calendário inicial
        self.criar_calendario()
        
        # Coluna direita - Eventos do dia
        right_frame = ttk.Frame(content_frame, style="Content.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Data selecionada
        date_frame = ttk.Frame(right_frame, style="Content.TFrame")
        date_frame.pack(fill=tk.X, pady=5)
        
        self.data_selecionada_var = tk.StringVar(value=datetime.datetime.now().strftime('%d/%m/%Y'))
        ttk.Label(
            date_frame,
            textvariable=self.data_selecionada_var,
            style="Subtitle.TLabel"
        ).pack(side=tk.LEFT)
        
        # Lista de eventos
        events_frame = ttk.LabelFrame(right_frame, text="Eventos do dia selecionado", padding=10)
        events_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para o texto e scrollbar
        events_text_frame = ttk.Frame(events_frame, style="Content.TFrame")
        events_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        events_scrollbar = ttk.Scrollbar(events_text_frame)
        events_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.eventos_dia = tk.Text(
            events_text_frame,
            wrap=tk.WORD,
            bg="white",
            bd=1,
            relief=tk.SOLID,
            font=("Arial", 10),
            height=15
        )
        self.eventos_dia.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.eventos_dia.configure(state='disabled')
        
        # Configurar scrollbar
        self.eventos_dia.config(yscrollcommand=events_scrollbar.set)
        events_scrollbar.config(command=self.eventos_dia.yview)
        
        # Botões de ação
        events_actions = ttk.Frame(right_frame, style="Content.TFrame")
        events_actions.pack(fill=tk.X, pady=10)
        
        # Botão com estilo personalizado para garantir contraste
        nova_tarefa_btn = tk.Button(
            events_actions,
            text="Nova Tarefa",
            bg="#3498db",  # Azul
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=lambda: self.nova_tarefa_calendario(self.data_selecionada_var.get())
        )
        nova_tarefa_btn.pack(side=tk.LEFT, padx=5)
    
    def criar_calendario(self):
        """Cria uma visualização de calendário"""
        # Limpar frame atual
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
        
        # Obter mês e ano selecionados
        mes_idx = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"].index(self.mes_var.get()) + 1
        ano = int(self.ano_var.get())
        
        # Cabeçalho dos dias da semana
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        
        # Frame para cabeçalho
        header_frame = ttk.Frame(self.cal_frame, style="Highlight.TFrame")
        header_frame.pack(fill=tk.X)
        
        # Adicionar cabeçalhos
        for i, dia in enumerate(dias_semana):
            lbl = ttk.Label(
                header_frame, 
                text=dia, 
                style="Subtitle.TLabel",
                width=6,
                anchor=tk.CENTER,
                padding=5
            )
            lbl.grid(row=0, column=i, padx=2, pady=2)
        
        # Determinar o primeiro dia do mês
        primeiro_dia = datetime.date(ano, mes_idx, 1)
        dia_semana_inicio = primeiro_dia.weekday()  # 0 é segunda-feira
        dia_semana_inicio = (dia_semana_inicio + 1) % 7  # Ajustar para domingo = 0
        
        # Determinar o número de dias no mês
        if mes_idx == 12:
            ultimo_dia = datetime.date(ano + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            ultimo_dia = datetime.date(ano, mes_idx + 1, 1) - datetime.timedelta(days=1)
        num_dias = ultimo_dia.day
        
        # Frame para os dias
        days_frame = ttk.Frame(self.cal_frame, style="Content.TFrame")
        days_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar grid de dias
        dia = 1
        for semana in range(6):  # Máximo de 6 semanas em um mês
            for dia_semana in range(7):
                if (semana == 0 and dia_semana < dia_semana_inicio) or (dia > num_dias):
                    # Célula vazia
                    lbl = ttk.Label(days_frame, text="", width=6, padding=5)
                    lbl.grid(row=semana, column=dia_semana, padx=2, pady=2)
                else:
                    # Criar botão para o dia
                    data_str = f"{dia:02d}/{mes_idx:02d}/{ano}"
                    
                    # Verificar se é o dia atual
                    hoje = datetime.datetime.now().date()
                    is_hoje = (dia == hoje.day and mes_idx == hoje.month and ano == hoje.year)
                    
                    # Botão com estilo personalizado para garantir contraste
                    if is_hoje:
                        btn = tk.Button(
                            days_frame, 
                            text=str(dia),
                            width=6,
                            bg="#3498db",  # Azul
                            fg="#ffffff",  # Branco
                            relief=tk.RAISED,
                            command=lambda d=data_str: self.selecionar_data(d)
                        )
                    else:
                        btn = tk.Button(
                            days_frame, 
                            text=str(dia),
                            width=6,
                            bg="#f5f5f5",  # Cinza claro
                            fg="#2c3e50",  # Azul escuro
                            relief=tk.RAISED,
                            command=lambda d=data_str: self.selecionar_data(d)
                        )
                    
                    btn.grid(row=semana, column=dia_semana, padx=2, pady=2)
                    dia += 1
                    
                    if dia > num_dias:
                        break
    
    def atualizar_calendario(self):
        """Atualiza a visualização do calendário"""
        self.criar_calendario()
    
    def selecionar_data(self, data_str):
        """Seleciona uma data no calendário"""
        self.data_selecionada_var.set(data_str)
        self.atualizar_eventos_dia(data_str)
    
    def ir_para_hoje(self):
        """Navega para a data atual no calendário"""
        hoje = datetime.datetime.now()
        self.mes_var.set(["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                          "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][hoje.month - 1])
        self.ano_var.set(str(hoje.year))
        self.atualizar_calendario()
        self.selecionar_data(hoje.strftime('%d/%m/%Y'))
    
    def processar_comando(self):
        """Processa o comando inserido pelo usuário"""
        comando = self.entrada.get()
        if not comando:
            return
        
        try:
            self.atualizar_status("Processando comando...")
            resultado = self.gerenciador.executar_comando(comando)
            self.atualizar_historico(f"> {comando}\n{resultado}\n{'='*50}\n")
            self.entrada.delete(0, tk.END)
            
            # Atualizar lista de tarefas se o comando for relacionado a tarefas
            if any(palavra in comando.lower() for palavra in ["adicionar", "lembrar", "excluir", "atualizar"]):
                self.carregar_tarefas()
                self.atualizar_eventos_dia(self.data_selecionada_var.get())
            
            self.atualizar_status("Comando executado com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar o comando:\n{str(e)}")
            self.atualizar_status("Erro ao processar comando")
    
    def atualizar_historico(self, texto):
        """Atualiza o histórico de comandos"""
        self.historico.configure(state='normal')
        self.historico.insert(tk.END, texto)
        self.historico.see(tk.END)
        self.historico.configure(state='disabled')
    
    def limpar_historico(self):
        """Limpa o histórico de comandos"""
        self.historico.configure(state='normal')
        self.historico.delete(1.0, tk.END)
        self.historico.configure(state='disabled')
    
    def mostrar_sugestoes(self):
        """Exibe sugestões de comandos com base no texto atual"""
        texto_atual = self.entrada.get().lower()
        sugestoes = []
        
        if not texto_atual:
            sugestoes = [
                "adicionar tarefa",
                "lembrar de",
                "listar tarefas",
                "agendar reunião"
            ]
        elif "adicionar" in texto_atual:
            sugestoes = [
                "adicionar reunião com equipe amanhã às 14h",
                "adicionar entrega de relatório sexta-feira",
                "adicionar consulta médica dia 15/06 às 10h"
            ]
        elif "lembrar" in texto_atual:
            sugestoes = [
                "lembrar de ligar para cliente amanhã às 9h",
                "lembrar de pagar conta de luz dia 10",
                "lembrar de comprar presente de aniversário"
            ]
        elif "listar" in texto_atual:
            sugestoes = [
                "listar tarefas de hoje",
                "listar tarefas da categoria trabalho",
                "listar tarefas de alta prioridade"
            ]
        elif "reunião" in texto_atual or "agendar" in texto_atual:
            sugestoes = [
                "agendar reunião de equipe amanhã às 15h",
                "agendar reunião com cliente na próxima segunda às 10h",
                "agendar videoconferência dia 05/06 às 16h"
            ]
        
        if sugestoes:
            # Criar janela de sugestões
            sugestoes_window = tk.Toplevel(self.root)
            sugestoes_window.title("Sugestões de Comandos")
            sugestoes_window.geometry("500x400")
            sugestoes_window.transient(self.root)
            sugestoes_window.grab_set()
            
            # Estilo da janela
            sugestoes_window.configure(bg=self.cor_fundo)
            
            # Título
            tk.Label(
                sugestoes_window,
                text="Selecione uma sugestão:",
                font=("Arial", 12, "bold"),
                bg=self.cor_fundo,
                fg=self.cor_texto,
                pady=10
            ).pack()
            
            # Frame para sugestões
            sugestoes_frame = tk.Frame(sugestoes_window, bg=self.cor_fundo, padx=20, pady=10)
            sugestoes_frame.pack(fill=tk.BOTH, expand=True)
            
            # Adicionar sugestões
            for sugestao in sugestoes:
                btn = tk.Button(
                    sugestoes_frame,
                    text=sugestao,
                    bg=self.cor_primaria,
                    fg="#ffffff",  # Branco para garantir contraste
                    relief=tk.RAISED,
                    padx=10,
                    pady=5,
                    font=("Arial", 10),
                    command=lambda s=sugestao: self.usar_sugestao(s, sugestoes_window)
                )
                btn.pack(fill=tk.X, pady=5)
                
                # Efeito hover
                btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.cor_secundaria))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.cor_primaria))
            
            # Botão cancelar
            tk.Button(
                sugestoes_window,
                text="Cancelar",
                bg="#95a5a6",
                fg="#ffffff",  # Branco para garantir contraste
                relief=tk.RAISED,
                padx=10,
                pady=5,
                font=("Arial", 10),
                command=sugestoes_window.destroy
            ).pack(pady=10)
    
    def usar_sugestao(self, sugestao, window=None):
        """Usa a sugestão selecionada"""
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, sugestao)
        if window:
            window.destroy()
    
    def usar_exemplo(self, exemplo):
        """Usa o exemplo de comando selecionado"""
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, exemplo)
        self.entrada.focus_set()
    
    def carregar_tarefas(self):
        """Carrega as tarefas do calendário para a interface"""
        try:
            self.atualizar_status("Carregando tarefas...")
            
            # Limpar lista atual
            for item in self.tarefas_tree.get_children():
                self.tarefas_tree.delete(item)
            
            # Obter eventos do calendário (próximos 30 dias)
            eventos = self.gerenciador.calendario.listar_eventos(max_resultados=30)
            self.tarefas = []
            
            # Processar eventos
            for evento in eventos:
                # Extrair informações
                id_evento = evento.get('id', '')
                titulo = evento.get('summary', 'Sem título')
                
                # Extrair data e hora
                try:
                    data_hora_str = evento.get('start', {}).get('dateTime', evento.get('start', {}).get('date', ''))
                    if 'T' in data_hora_str:
                        # Formato com hora (2023-05-28T14:00:00+00:00)
                        data_hora = datetime.datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
                        data = data_hora.strftime('%d/%m/%Y')
                        hora = data_hora.strftime('%H:%M')
                    else:
                        # Formato só com data (2023-05-28)
                        data = datetime.datetime.strptime(data_hora_str, '%Y-%m-%d').strftime('%d/%m/%Y')
                        hora = ""
                except:
                    data = "Data desconhecida"
                    hora = ""
                
                # Extrair categoria pela cor
                cor_evento = evento.get('colorId', '5')
                categorias_cores = {
                    "11": "trabalho",
                    "9": "pessoal",
                    "7": "estudo",
                    "5": "geral"
                }
                categoria = categorias_cores.get(cor_evento, "geral")
                
                # Extrair prioridade do título
                prioridade = "normal"
                if titulo.startswith("⚠️"):
                    prioridade = "alta"
                    titulo = titulo[2:].strip()
                elif titulo.startswith("⚡"):
                    prioridade = "média"
                    titulo = titulo[2:].strip()
                elif titulo.startswith("🔹"):
                    prioridade = "baixa"
                    titulo = titulo[2:].strip()
                
                # Adicionar à lista de tarefas
                tarefa = {
                    'id': id_evento,
                    'titulo': titulo,
                    'data': data,
                    'hora': hora,
                    'categoria': categoria,
                    'prioridade': prioridade,
                    'descricao': evento.get('description', ''),
                    'local': evento.get('location', '')
                }
                self.tarefas.append(tarefa)
                
                # Adicionar ao treeview
                self.tarefas_tree.insert(
                    "",
                    tk.END,
                    values=(id_evento, titulo, data, hora, categoria, prioridade)
                )
            
            self.atualizar_status(f"Carregadas {len(self.tarefas)} tarefas")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar tarefas:\n{str(e)}")
            self.atualizar_status("Erro ao carregar tarefas")
    
    def filtrar_tarefas(self):
        """Filtra as tarefas de acordo com os critérios selecionados"""
        categoria = self.categoria_var.get()
        prioridade = self.prioridade_var.get()
        data_filtro = self.data_filtro_var.get().strip()
        
        # Limpar lista atual
        for item in self.tarefas_tree.get_children():
            self.tarefas_tree.delete(item)
        
        # Aplicar filtros
        for tarefa in self.tarefas:
            if (categoria == "todas" or tarefa['categoria'] == categoria) and \
               (prioridade == "todas" or tarefa['prioridade'] == prioridade) and \
               (not data_filtro or tarefa['data'] == data_filtro):
                self.tarefas_tree.insert(
                    "",
                    tk.END,
                    values=(tarefa['id'], tarefa['titulo'], tarefa['data'], tarefa['hora'], tarefa['categoria'], tarefa['prioridade'])
                )
    
    def limpar_filtros(self):
        """Limpa todos os filtros aplicados"""
        self.categoria_var.set("todas")
        self.prioridade_var.set("todas")
        self.data_filtro_var.set("")
        
        # Recarregar todas as tarefas
        self.carregar_tarefas()
    
    def mostrar_detalhes_tarefa(self, event=None):
        """Exibe os detalhes da tarefa selecionada"""
        selecionado = self.tarefas_tree.selection()
        if not selecionado:
            return
        
        # Obter valores da linha selecionada
        valores = self.tarefas_tree.item(selecionado, "values")
        id_tarefa = valores[0]
        
        # Buscar tarefa na lista
        tarefa = next((t for t in self.tarefas if t['id'] == id_tarefa), None)
        if not tarefa:
            return
        
        # Exibir detalhes
        self.detalhes_tarefa.configure(state='normal')
        self.detalhes_tarefa.delete(1.0, tk.END)
        
        # Formatação com ícones de prioridade
        icone = ""
        if tarefa['prioridade'] == "alta":
            icone = "⚠️ "
        elif tarefa['prioridade'] == "média":
            icone = "⚡ "
        elif tarefa['prioridade'] == "baixa":
            icone = "🔹 "
        
        detalhes = f"Título: {icone}{tarefa['titulo']}\n"
        detalhes += f"Data: {tarefa['data']} às {tarefa['hora'] if tarefa['hora'] else 'Não especificado'}\n"
        detalhes += f"Categoria: {tarefa['categoria']}\n"
        detalhes += f"Prioridade: {tarefa['prioridade']}\n"
        
        if tarefa['local']:
            detalhes += f"Local: {tarefa['local']}\n"
        
        if tarefa['descricao']:
            detalhes += f"\nDescrição:\n{tarefa['descricao']}"
        
        self.detalhes_tarefa.insert(1.0, detalhes)
        self.detalhes_tarefa.configure(state='disabled')
    
    def nova_tarefa(self):
        """Abre janela para criar nova tarefa"""
        self.abrir_janela_tarefa()
    
    def nova_tarefa_calendario(self, data_str):
        """Cria nova tarefa a partir da data selecionada no calendário"""
        try:
            # Converter string para objeto date
            partes = data_str.split('/')
            data = datetime.date(int(partes[2]), int(partes[1]), int(partes[0]))
            self.abrir_janela_tarefa(data)
        except:
            self.abrir_janela_tarefa()
    
    def editar_tarefa(self):
        """Edita a tarefa selecionada"""
        selecionado = self.tarefas_tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione uma tarefa para editar")
            return
        
        self.editar_tarefa_selecionada()
    
    def editar_tarefa_selecionada(self, event=None):
        """Abre janela para editar a tarefa selecionada"""
        selecionado = self.tarefas_tree.selection()
        if not selecionado:
            return
        
        # Obter valores da linha selecionada
        valores = self.tarefas_tree.item(selecionado, "values")
        id_tarefa = valores[0]
        
        # Buscar tarefa na lista
        tarefa = next((t for t in self.tarefas if t['id'] == id_tarefa), None)
        if not tarefa:
            return
        
        self.abrir_janela_tarefa(editar=True, tarefa=tarefa)
    
    def abrir_janela_tarefa(self, data=None, editar=False, tarefa=None):
        """Abre janela para criar ou editar tarefa"""
        # Criar janela
        janela = tk.Toplevel(self.root)
        janela.title("Nova Tarefa" if not editar else "Editar Tarefa")
        janela.geometry("600x550")
        janela.transient(self.root)
        janela.grab_set()
        
        # Estilo da janela
        janela.configure(bg=self.cor_fundo)
        
        # Variáveis
        var_titulo = tk.StringVar(value=tarefa['titulo'] if editar and tarefa else "")
        var_categoria = tk.StringVar(value=tarefa['categoria'] if editar and tarefa else "trabalho")
        var_prioridade = tk.StringVar(value=tarefa['prioridade'] if editar and tarefa else "normal")
        
        if editar and tarefa:
            # Converter string de data para objeto date
            try:
                partes = tarefa['data'].split('/')
                data = datetime.date(int(partes[2]), int(partes[1]), int(partes[0]))
            except:
                data = datetime.date.today()
            
            # Converter string de hora para tupla (hora, minuto)
            try:
                if tarefa['hora']:
                    partes_hora = tarefa['hora'].split(':')
                    hora = int(partes_hora[0])
                    minuto = int(partes_hora[1])
                else:
                    hora = 9
                    minuto = 0
            except:
                hora = 9
                minuto = 0
        else:
            # Data padrão
            if data is None:
                data = datetime.date.today()
            
            # Hora padrão (9:00)
            hora = 9
            minuto = 0
        
        # Frame principal
        main_frame = ttk.Frame(janela, style="Content.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título da janela
        ttk.Label(
            main_frame,
            text="Nova Tarefa" if not editar else "Editar Tarefa",
            style="Title.TLabel"
        ).pack(pady=(0, 20))
        
        # Título da tarefa
        ttk.Label(
            main_frame,
            text="Título da tarefa:",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        ttk.Entry(
            main_frame,
            textvariable=var_titulo,
            width=50,
            font=("Arial", 11)
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Data e hora
        data_hora_frame = ttk.Frame(main_frame, style="Content.TFrame")
        data_hora_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Data
        data_frame = ttk.Frame(data_hora_frame, style="Content.TFrame")
        data_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(
            data_frame,
            text="Data (DD/MM/AAAA):",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        var_data = tk.StringVar(value=data.strftime('%d/%m/%Y'))
        ttk.Entry(
            data_frame,
            textvariable=var_data,
            width=15
        ).pack(fill=tk.X)
        
        # Hora
        hora_frame = ttk.Frame(data_hora_frame, style="Content.TFrame")
        hora_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            hora_frame,
            text="Hora (HH:MM):",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        var_hora = tk.StringVar(value=f"{hora:02d}:{minuto:02d}")
        ttk.Entry(
            hora_frame,
            textvariable=var_hora,
            width=10
        ).pack(fill=tk.X)
        
        # Categoria e prioridade
        cat_prio_frame = ttk.Frame(main_frame, style="Content.TFrame")
        cat_prio_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Categoria
        cat_frame = ttk.Frame(cat_prio_frame, style="Content.TFrame")
        cat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(
            cat_frame,
            text="Categoria:",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        categorias = ["trabalho", "pessoal", "estudo", "geral"]
        ttk.Combobox(
            cat_frame,
            textvariable=var_categoria,
            values=categorias,
            state="readonly",
            width=15
        ).pack(fill=tk.X)
        
        # Prioridade
        prio_frame = ttk.Frame(cat_prio_frame, style="Content.TFrame")
        prio_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            prio_frame,
            text="Prioridade:",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        prioridades = ["alta", "média", "baixa", "normal"]
        ttk.Combobox(
            prio_frame,
            textvariable=var_prioridade,
            values=prioridades,
            state="readonly",
            width=15
        ).pack(fill=tk.X)
        
        # Local
        ttk.Label(
            main_frame,
            text="Local (opcional):",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        var_local = tk.StringVar(value=tarefa['local'] if editar and tarefa else "")
        ttk.Entry(
            main_frame,
            textvariable=var_local,
            width=50,
            font=("Arial", 11)
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Descrição
        ttk.Label(
            main_frame,
            text="Descrição:",
            padding=(0, 5)
        ).pack(anchor=tk.W)
        
        # Frame para o texto e scrollbar
        desc_frame = ttk.Frame(main_frame, style="Content.TFrame")
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Scrollbar
        desc_scrollbar = ttk.Scrollbar(desc_frame)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        txt_descricao = tk.Text(
            desc_frame,
            wrap=tk.WORD,
            bg="white",
            bd=1,
            relief=tk.SOLID,
            font=("Arial", 10),
            height=8
        )
        txt_descricao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scrollbar
        txt_descricao.config(yscrollcommand=desc_scrollbar.set)
        desc_scrollbar.config(command=txt_descricao.yview)
        
        if editar and tarefa and tarefa.get('descricao'):
            txt_descricao.insert(1.0, tarefa['descricao'])
        
        # Botões de ação
        botoes_frame = ttk.Frame(main_frame, style="Content.TFrame")
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        def salvar_tarefa():
            try:
                # Validar campos
                titulo = var_titulo.get().strip()
                if not titulo:
                    messagebox.showerror("Erro", "O título da tarefa é obrigatório")
                    return
                
                # Obter valores
                categoria = var_categoria.get()
                prioridade = var_prioridade.get()
                local = var_local.get().strip()
                descricao = txt_descricao.get(1.0, tk.END).strip()
                
                # Formatar data e hora
                data_formatada = var_data.get()
                hora_formatada = var_hora.get()
                
                # Validar data
                if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_formatada):
                    messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
                    return
                
                # Validar hora
                if hora_formatada and not re.match(r'^\d{1,2}:\d{2}$', hora_formatada):
                    messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")
                    return
                
                # Criar comando para o gerenciador
                if editar and tarefa:
                    comando = f"atualizar tarefa id:{tarefa['id']} {titulo} {data_formatada} {hora_formatada} categoria:{categoria} prioridade:{prioridade}"
                else:
                    comando = f"adicionar {titulo} {data_formatada} {hora_formatada} categoria:{categoria} prioridade:{prioridade}"
                
                if local:
                    comando += f" local:{local}"
                
                # Executar comando
                resultado = self.gerenciador.executar_comando(comando)
                
                # Atualizar interface
                self.carregar_tarefas()
                self.atualizar_eventos_dia(self.data_selecionada_var.get())
                
                # Fechar janela
                janela.destroy()
                
                # Mostrar resultado
                messagebox.showinfo("Sucesso", "Tarefa salva com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar tarefa:\n{str(e)}")
        
        # Botões com estilo personalizado para garantir contraste
        salvar_btn = tk.Button(
            botoes_frame,
            text="Salvar",
            bg="#3498db",  # Azul
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=salvar_tarefa
        )
        salvar_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        cancelar_btn = tk.Button(
            botoes_frame,
            text="Cancelar",
            bg="#95a5a6",  # Cinza
            fg="#ffffff",  # Branco
            relief=tk.RAISED,
            command=janela.destroy
        )
        cancelar_btn.pack(side=tk.LEFT)
    
    def excluir_tarefa(self):
        """Exclui a tarefa selecionada"""
        selecionado = self.tarefas_tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione uma tarefa para excluir")
            return
        
        try:
            # Obter valores da linha selecionada
            valores = self.tarefas_tree.item(selecionado, "values")
            id_tarefa = valores[0]
            titulo = valores[1]
            
            # Confirmar exclusão
            confirmacao = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a tarefa:\n{titulo}?"
            )
            
            if not confirmacao:
                return
            
            # Executar comando de exclusão
            comando = f"excluir tarefa id:{id_tarefa}"
            resultado = self.gerenciador.executar_comando(comando)
            
            # Atualizar interface
            self.carregar_tarefas()
            self.atualizar_eventos_dia(self.data_selecionada_var.get())
            
            # Mostrar resultado
            messagebox.showinfo("Sucesso", "Tarefa excluída com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir tarefa:\n{str(e)}")
    
    def atualizar_eventos_dia(self, data_str=None):
        """Atualiza a lista de eventos do dia selecionado"""
        if data_str is None:
            data_str = self.data_selecionada_var.get()
        
        try:
            # Filtrar tarefas pela data
            tarefas_do_dia = [t for t in self.tarefas if t['data'] == data_str]
            
            # Ordenar por hora
            tarefas_do_dia.sort(key=lambda t: t['hora'] if t['hora'] else "")
            
            # Atualizar área de texto
            self.eventos_dia.configure(state='normal')
            self.eventos_dia.delete(1.0, tk.END)
            
            if not tarefas_do_dia:
                self.eventos_dia.insert(1.0, f"Nenhum evento para {data_str}")
            else:
                self.eventos_dia.insert(1.0, f"Eventos para {data_str}:\n\n")
                
                for i, tarefa in enumerate(tarefas_do_dia, 1):
                    # Formatação com ícones de prioridade
                    icone = ""
                    if tarefa['prioridade'] == "alta":
                        icone = "⚠️ "
                    elif tarefa['prioridade'] == "média":
                        icone = "⚡ "
                    elif tarefa['prioridade'] == "baixa":
                        icone = "🔹 "
                    
                    # Inserir título com tag para formatação
                    self.eventos_dia.insert(tk.END, f"{i}. ", "numero")
                    self.eventos_dia.insert(tk.END, f"{icone}{tarefa['titulo']}\n", "titulo")
                    
                    # Inserir detalhes
                    self.eventos_dia.insert(tk.END, f"   Horário: ", "campo")
                    self.eventos_dia.insert(tk.END, f"{tarefa['hora'] if tarefa['hora'] else 'Não especificado'}\n", "valor")
                    
                    self.eventos_dia.insert(tk.END, f"   Categoria: ", "campo")
                    self.eventos_dia.insert(tk.END, f"{tarefa['categoria']}\n", "valor")
                    
                    if tarefa['local']:
                        self.eventos_dia.insert(tk.END, f"   Local: ", "campo")
                        self.eventos_dia.insert(tk.END, f"{tarefa['local']}\n", "valor")
                    
                    self.eventos_dia.insert(tk.END, "\n")
            
            # Configurar tags para formatação
            self.eventos_dia.tag_configure("titulo", font=("Arial", 10, "bold"))
            self.eventos_dia.tag_configure("numero", font=("Arial", 10, "bold"))
            self.eventos_dia.tag_configure("campo", font=("Arial", 9), foreground="#555555")
            self.eventos_dia.tag_configure("valor", font=("Arial", 9))
            
            self.eventos_dia.configure(state='disabled')
        except Exception as e:
            print(f"Erro ao atualizar eventos do dia: {str(e)}")
            # Não mostrar messagebox para evitar interrupções na inicialização
    
    def atualizar_status(self, mensagem):
        """Atualiza a barra de status"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=mensagem)
            self.root.update_idletasks()
    
    def executar(self):
        """Inicia a execução da interface gráfica"""
        self.root.mainloop()

if __name__ == "__main__":
    app = AssistenteGUIModerno()
    app.executar()