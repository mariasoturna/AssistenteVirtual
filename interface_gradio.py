from datetime import datetime
import gradio as gr

# Lista de eventos simulada
eventos = []

def adicionar_evento(titulo, data, hora):
    if not titulo or not data or not hora:
        return "Por favor, preencha todos os campos."
    
    try:
        dt = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "Formato inválido. Use data AAAA-MM-DD e hora HH:MM."

    eventos.append({
        "titulo": titulo,
        "datahora": dt
    })
    return f"✅ Evento '{titulo}' adicionado para {dt.strftime('%d/%m/%Y %H:%M')}."

def listar_eventos():
    if not eventos:
        return "Nenhum evento cadastrado."
    eventos_ordenados = sorted(eventos, key=lambda x: x["datahora"])
    return "\n".join([f"{ev['datahora'].strftime('%d/%m/%Y %H:%M')} - {ev['titulo']}" for ev in eventos_ordenados])

def deletar_eventos():
    eventos.clear()
    return "🗑️ Todos os eventos foram removidos."

# Componentes de entrada
titulo = gr.Textbox(label="Título do Evento")
data = gr.Textbox(label="Data (AAAA-MM-DD)")
hora = gr.Textbox(label="Hora (HH:MM)")

# Interface principal
interface = gr.Interface(
    fn=adicionar_evento,
    inputs=[titulo, data, hora],
    outputs=gr.Textbox(label="Resultado"),
    title="🧠 Assistente Virtual de Tarefas",
    description="Adicione, liste e exclua seus eventos com facilidade.",
    allow_flagging="never"
)

# Adicionando botões extras via `Interface` não é direto, então vamos usar `.launch()` com `live=True`
def launch_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# 🧠 Assistente Virtual de Tarefas")

        with gr.Row():
            t = gr.Textbox(label="Título do Evento")
        with gr.Row():
            d = gr.Textbox(label="Data (AAAA-MM-DD)")
            h = gr.Textbox(label="Hora (HH:MM)")

        out = gr.Textbox(label="Resultado", lines=10)

        with gr.Row():
            gr.Button("Adicionar Evento").click(adicionar_evento, inputs=[t, d, h], outputs=out)
            gr.Button("Listar Eventos").click(listar_eventos, outputs=out)
            gr.Button("Deletar Todos").click(deletar_eventos, outputs=out)

    demo.launch()

if __name__ == "__main__":
     interface.launch(server_port=8080, server_name="0.0.0.0")

