import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from datetime import datetime
import os
import sys

eventos = []  # lista simulada
NOTAS_ARQUIVO = "notas.txt"

# --------------------------------------------------------------------
# Funções do BLOCO DE NOTAS
# --------------------------------------------------------------------

def abrir_bloconotas():
    janela_notas = Toplevel()
    janela_notas.title("Bloco de Notas")
    janela_notas.geometry("500x400")

    tk.Label(janela_notas, text="Bloco de Notas:", font=("Arial", 12, "bold")).pack(pady=5)

    caixa_texto = tk.Text(janela_notas, wrap="word", font=("Arial", 11))
    caixa_texto.pack(fill="both", expand=True, padx=10, pady=10)

    # Carregar texto existente, se houver
    if os.path.exists(NOTAS_ARQUIVO):
        with open(NOTAS_ARQUIVO, "r", encoding="utf-8") as f:
            caixa_texto.insert("1.0", f.read())

    # Botões
    def salvar():
        conteudo = caixa_texto.get("1.0", tk.END)
        with open(NOTAS_ARQUIVO, "w", encoding="utf-8") as f:
            f.write(conteudo)
        messagebox.showinfo("Sucesso", "Notas salvas!")

    def carregar():
        if os.path.exists(NOTAS_ARQUIVO):
            with open(NOTAS_ARQUIVO, "r", encoding="utf-8") as f:
                caixa_texto.delete("1.0", tk.END)
                caixa_texto.insert("1.0", f.read())
        else:
            messagebox.showinfo("Aviso", "Nenhuma nota salva ainda.")

    def limpar():
        caixa_texto.delete("1.0", tk.END)

    frame_botoes = tk.Frame(janela_notas)
    frame_botoes.pack(pady=8)

    tk.Button(frame_botoes, text="Salvar", width=10, command=salvar).grid(row=0, column=0, padx=5)
    tk.Button(frame_botoes, text="Carregar", width=10, command=carregar).grid(row=0, column=1, padx=5)
    tk.Button(frame_botoes, text="Limpar", width=10, command=limpar).grid(row=0, column=2, padx=5)


# --------------------------------------------------------------------
# Funções do GERENCIAMENTO DE EVENTOS
# --------------------------------------------------------------------

def adicionar_evento():
    titulo = entry_titulo.get()
    data = entry_data.get()
    hora = entry_hora.get()

    if not (titulo and data and hora):
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    try:
        datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Erro", "Formato de data ou hora inválido.")
        return

    eventos.append({"titulo": titulo, "data": data, "hora": hora})
    messagebox.showinfo("Sucesso", f"Evento '{titulo}' adicionado!")
    entry_titulo.delete(0, tk.END)
    entry_data.delete(0, tk.END)
    entry_hora.delete(0, tk.END)


def listar_eventos():
    if not eventos:
        messagebox.showinfo("Eventos", "Nenhum evento cadastrado.")
        return

    texto = ""
    for i, ev in enumerate(eventos):
        texto += f"{i+1}. {ev['titulo']} - {ev['data']} às {ev['hora']}\n"

    messagebox.showinfo("Eventos", texto)


def deletar_evento():
    idx = simpledialog.askstring("Deletar", "Número do evento a deletar:")

    if not idx:
        return

    try:
        idx = int(idx) - 1
        removido = eventos.pop(idx)
        messagebox.showinfo("Sucesso", f"Evento '{removido['titulo']}' removido.")
    except:
        messagebox.showerror("Erro", "Índice inválido.")


def editar_evento():
    idx = simpledialog.askstring("Editar", "Número do evento a editar:")
    if not idx:
        return

    try:
        idx = int(idx) - 1
        evento = eventos[idx]
    except:
        messagebox.showerror("Erro", "Índice inválido.")
        return

    novo_titulo = simpledialog.askstring("Editar", "Novo título:", initialvalue=evento['titulo'])
    nova_data = simpledialog.askstring("Editar", "Nova data (AAAA-MM-DD):", initialvalue=evento['data'])
    nova_hora = simpledialog.askstring("Editar", "Nova hora (HH:MM):", initialvalue=evento['hora'])

    if not (novo_titulo and nova_data and nova_hora):
        messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
        return

    eventos[idx] = {
        "titulo": novo_titulo,
        "data": nova_data,
        "hora": nova_hora
    }

    messagebox.showinfo("Sucesso", "Evento atualizado com sucesso!")


def deletar_todos():
    if messagebox.askyesno("Confirmar", "Deseja realmente deletar TODOS os eventos?"):
        eventos.clear()
        messagebox.showinfo("Sucesso", "Todos os eventos foram apagados.")


# --------------------------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------------------------

janela = tk.Tk()
janela.title("Assistente Virtual de Tarefas")

# --- CONFIGURAÇÃO DO ÍCONE ---
if getattr(sys, 'frozen', False):  
    icone_path = os.path.join(sys._MEIPASS, "icon_task_folder.ico")
else:
    icone_path = "icon_task_folder.ico"

try:
    janela.iconbitmap("icon_task_folder.ico")
except:
    pass

janela.geometry("350x350")

tk.Label(janela, text="Título do Evento:").pack()
entry_titulo = tk.Entry(janela)
entry_titulo.pack()

tk.Label(janela, text="Data (AAAA-MM-DD):").pack()
entry_data = tk.Entry(janela)
entry_data.pack()

tk.Label(janela, text="Hora (HH:MM):").pack()
entry_hora = tk.Entry(janela)
entry_hora.pack()

tk.Button(janela, text="Adicionar Evento", command=adicionar_evento).pack(pady=5)
tk.Button(janela, text="Listar Eventos", command=listar_eventos).pack(pady=5)
tk.Button(janela, text="Editar Evento", command=editar_evento).pack(pady=5)
tk.Button(janela, text="Deletar Evento", command=deletar_evento).pack(pady=5)
tk.Button(janela, text="Deletar Todos", command=deletar_todos).pack(pady=5)

# 🔥 Botão do bloco de notas
tk.Button(janela, text="📝 Bloco de Notas", command=abrir_bloconotas).pack(pady=10)

janela.mainloop()