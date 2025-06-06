import gradio as gr
from datetime import datetime

# Lista simulada de eventos
eventos = []

# Função para adicionar evento
def adicionar_evento(titulo, data, hora):
    if not (titulo and data and hora):
        return "Por favor, preencha todos os campos."
    
    try:
        datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "Data ou hora em formato inválido."

    evento = {"titulo": titulo, "data": data, "hora": hora}
    eventos.append(evento)
    return f"Evento '{titulo}' adicionado com sucesso!"

# Função para listar eventos
def listar_eventos():
    if not eventos:
        return "Nenhum evento encontrado."
    
    texto = "Eventos cadastrados:\n\n"
    for idx, e in enumerate(eventos):
        texto += f"{idx+1}. {e['titulo']} - {e['data']} às {e['hora']}\n"
    return texto

# Função para deletar todos os eventos
def deletar_todos():
    eventos.clear()
    return "Todos os eventos foram removidos."

# Função para deletar evento específico
def deletar_evento(index):
    try:
        index = int(index) - 1
        removido = eventos.pop(index)
        return f"Evento '{removido['titulo']}' removido."
    except:
        return "Índice inválido."

# Função para editar evento
def editar_evento(index, novo_titulo, nova_data, nova_hora):
    try:
        index = int(index) - 1
        eventos[index] = {
            "titulo": novo_titulo,
            "data": nova_data,
            "hora": nova_hora
        }
        return f"Evento {index+1} atualizado com sucesso."
    except:
        return "Erro ao editar evento. Verifique os dados."

# Interface Gradio
def launch_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# 🧠 Assistente Virtual de Tarefas")

        with gr.Tab("Adicionar Evento"):
            titulo = gr.Textbox(label="Título do Evento")
            data = gr.Textbox(label="Data (AAAA-MM-DD)")
            hora = gr.Textbox(label="Hora (HH:MM)")
            btn_add = gr.Button("Adicionar")
            saida_add = gr.Textbox(label="Resultado")
            btn_add.click(adicionar_evento, [titulo, data, hora], saida_add)

        with gr.Tab("Listar Eventos"):
            btn_list = gr.Button("Listar Todos")
            saida_list = gr.Textbox(label="Eventos", lines=10)
            btn_list.click(listar_eventos, outputs=saida_list)

        with gr.Tab("Editar Evento"):
            idx_edit = gr.Textbox(label="Número do Evento a Editar")
            novo_titulo = gr.Textbox(label="Novo Título")
            nova_data = gr.Textbox(label="Nova Data (AAAA-MM-DD)")
            nova_hora = gr.Textbox(label="Nova Hora (HH:MM)")
            btn_edit = gr.Button("Editar Evento")
            saida_edit = gr.Textbox(label="Resultado")
            btn_edit.click(editar_evento, [idx_edit, novo_titulo, nova_data, nova_hora], saida_edit)

        with gr.Tab("Deletar Evento"):
            idx_del = gr.Textbox(label="Número do Evento a Deletar")
            btn_del = gr.Button("Deletar")
            saida_del = gr.Textbox(label="Resultado")
            btn_del.click(deletar_evento, idx_del, saida_del)

        with gr.Tab("Deletar Todos"):
            btn_clear = gr.Button("Deletar Todos os Eventos")
            saida_clear = gr.Textbox(label="Resultado")
            btn_clear.click(deletar_todos, outputs=saida_clear)

    return demo

# Executa
if __name__ == "__main__":
    interface = launch_interface()
    interface.launch()
