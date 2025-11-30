import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from datetime import datetime
import os
import sys

eventos = []
NOTAS_ARQUIVO = "notas.txt"

# ==========================================================
# 🔵 FUNÇÃO AUXILIAR: escrever no bloco de notas
# ==========================================================
def registrar_nota(texto):
    with open(NOTAS_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{texto}\n")

# ==========================================================
# 🔵 FUNÇÕES DE EVENTOS
# ==========================================================
def adicionar_evento():
    titulo = entry_titulo.get()
    data = entry_data.get()
    hora = entry_hora.get()

    if not (titulo and data and hora):
        status_label.config(text="⚠ Preencha todos os campos.", bootstyle=WARNING)
        return

    try:
        datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        status_label.config(text="❌ Data ou hora inválida.", bootstyle=DANGER)
        return

    eventos.append({"titulo": titulo, "data": data, "hora": hora})
    status_label.config(text=f"✔ Evento '{titulo}' adicionado!", bootstyle=SUCCESS)

    registrar_nota(f"[ADICIONADO] {titulo} - {data} às {hora}")

    entry_titulo.delete(0, "end")
    entry_data.delete(0, "end")
    entry_hora.delete(0, "end")
    atualizar_lista_eventos()

def atualizar_lista_eventos():
    caixa_eventos.delete("1.0", "end")
    if not eventos:
        caixa_eventos.insert("1.0", "Nenhum evento cadastrado.")
        return
    for i, ev in enumerate(eventos):
        caixa_eventos.insert("end", f"{i+1}. {ev['titulo']} - {ev['data']} às {ev['hora']}\n")

def deletar_evento():
    idx = simpledialog.askstring("Deletar", "Número do evento a deletar:")
    if not idx:
        return
    try:
        idx = int(idx) - 1
        removido = eventos.pop(idx)
        status_label2.config(text=f"✔ '{removido['titulo']}' removido!", bootstyle=SUCCESS)
        registrar_nota(f"[REMOVIDO] {removido['titulo']} - {removido['data']} às {removido['hora']}")
        atualizar_lista_eventos()
    except:
        status_label2.config(text="❌ Índice inválido.", bootstyle=DANGER)

def editar_evento():
    idx = simpledialog.askstring("Editar", "Número do evento a editar:")
    if not idx:
        return
    try:
        idx = int(idx) - 1
        evento = eventos[idx]
    except:
        status_label2.config(text="❌ Índice inválido.", bootstyle=DANGER)
        return

    novo_titulo = simpledialog.askstring("Editar", "Novo título:", initialvalue=evento['titulo'])
    nova_data = simpledialog.askstring("Editar", "Nova data (AAAA-MM-DD):", initialvalue=evento['data'])
    nova_hora = simpledialog.askstring("Editar", "Nova hora (HH:MM):", initialvalue=evento['hora'])

    if not (novo_titulo and nova_data and nova_hora):
        status_label2.config(text="⚠ Todos os campos são obrigatórios.", bootstyle=WARNING)
        return

    registrar_nota(
        f"[EDITADO] {evento['titulo']} -> {novo_titulo} "
        f"| {evento['data']} {evento['hora']} -> {nova_data} {nova_hora}"
    )

    eventos[idx] = {"titulo": novo_titulo, "data": nova_data, "hora": nova_hora}
    status_label2.config(text="✔ Evento atualizado!", bootstyle=SUCCESS)
    atualizar_lista_eventos()

def deletar_todos():
    if messagebox.askyesno("Confirmar", "Deseja apagar TODOS os eventos?"):
        for ev in eventos:
            registrar_nota(f"[REMOVIDO] {ev['titulo']} - {ev['data']} às {ev['hora']}")
        eventos.clear()
        atualizar_lista_eventos()
        status_label2.config(text="✔ Todos os eventos foram removidos!", bootstyle=SUCCESS)

# ==========================================================
# 🔵 FUNÇÕES DO BLOCO DE NOTAS (integrado na interface)
# ==========================================================
def carregar_notas():
    if os.path.exists(NOTAS_ARQUIVO):
        with open(NOTAS_ARQUIVO, "r", encoding="utf-8") as f:
            notas_text.delete("1.0", "end")
            notas_text.insert("1.0", f.read())

def salvar_notas():
    with open(NOTAS_ARQUIVO, "w", encoding="utf-8") as f:
        f.write(notas_text.get("1.0", "end"))
    status_notas.config(text="✔ Notas salvas!", bootstyle=SUCCESS)

def limpar_notas():
    notas_text.delete("1.0", "end")

# ==========================================================
# 🔵 INTERFACE PRINCIPAL (ttkbootstrap moderna)
# ==========================================================
janela = ttk.Window(themename="superhero")
janela.title("Assistente Virtual de Tarefas")
janela.geometry("550x600")
janela.resizable(False, False)

notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ------------------ TAB 1: ADICIONAR EVENTO ------------------
tab_add = ttk.Frame(notebook)
notebook.add(tab_add, text="➕ Criar Evento")

ttk.Label(tab_add, text="Adicionar Evento", font=("Segoe UI", 18, "bold")).pack(pady=10)

frame_add = ttk.Frame(tab_add, padding=15)
frame_add.pack(fill="both", expand=True)

ttk.Label(frame_add, text="Título:").pack(anchor="w")
entry_titulo = ttk.Entry(frame_add)
entry_titulo.pack(fill="x", pady=5)

ttk.Label(frame_add, text="Data (AAAA-MM-DD):").pack(anchor="w")
entry_data = ttk.Entry(frame_add)
entry_data.pack(fill="x", pady=5)

ttk.Label(frame_add, text="Hora (HH:MM):").pack(anchor="w")
entry_hora = ttk.Entry(frame_add)
entry_hora.pack(fill="x", pady=5)

ttk.Button(frame_add, text="Adicionar Evento", bootstyle=SUCCESS, command=adicionar_evento).pack(fill="x", pady=10)

status_label = ttk.Label(frame_add, text="", font=("Segoe UI", 10))
status_label.pack()

# ------------------ TAB 2: GERENCIAR EVENTOS ------------------
tab_list = ttk.Frame(notebook)
notebook.add(tab_list, text="📋 Gerenciar Eventos")

ttk.Label(tab_list, text="Eventos Cadastrados", font=("Segoe UI", 18, "bold")).pack(pady=10)

caixa_eventos = ttk.Text(tab_list, height=15, font=("Segoe UI", 11))
caixa_eventos.pack(fill="both", padx=15, pady=10)

bot_frame = ttk.Frame(tab_list)
bot_frame.pack(pady=10)

ttk.Button(bot_frame, text="Editar", width=13, bootstyle=WARNING, command=editar_evento).grid(row=0, column=0, padx=5)
ttk.Button(bot_frame, text="Deletar", width=13, bootstyle=DANGER, command=deletar_evento).grid(row=0, column=1, padx=5)
ttk.Button(bot_frame, text="Deletar Todos", width=13, bootstyle=DARK, command=deletar_todos).grid(row=0, column=2, padx=5)

status_label2 = ttk.Label(tab_list, text="")
status_label2.pack()

atualizar_lista_eventos()

# ------------------ TAB 3: BLOCO DE NOTAS ------------------
tab_notas = ttk.Frame(notebook)
notebook.add(tab_notas, text="📝 Bloco de Notas")

ttk.Label(tab_notas, text="Bloco de Notas", font=("Segoe UI", 18, "bold")).pack(pady=10)

notas_text = ttk.Text(tab_notas, wrap="word", font=("Segoe UI", 11))
notas_text.pack(fill="both", expand=True, padx=15, pady=10)

btn_frame_notas = ttk.Frame(tab_notas)
btn_frame_notas.pack(pady=10)

ttk.Button(btn_frame_notas, text="Salvar", width=13, bootstyle=SUCCESS, command=salvar_notas).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame_notas, text="Limpar", width=13, bootstyle=DANGER, command=limpar_notas).grid(row=0, column=1, padx=5)

status_notas = ttk.Label(tab_notas, text="")
status_notas.pack()

carregar_notas()

janela.mainloop()