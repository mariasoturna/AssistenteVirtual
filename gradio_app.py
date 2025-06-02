import gradio as gr
from utils.calendario.google import GerenciadorCalendarioGoogle
from datetime import datetime

cal = GerenciadorCalendarioGoogle()

def criar_evento(titulo, inicio, fim, descricao, local, cor):
    try:
        evento_id = cal.adicionar_evento(titulo, inicio, fim, descricao, local, cor or None)
        return f"✅ Evento criado com sucesso! ID: {evento_id}"
    except Exception as e:
        return f"❌ Erro ao criar evento: {str(e)}"

def listar_eventos(max_resultados):
    try:
        eventos = cal.listar_eventos(max_resultados=int(max_resultados))
        if not eventos:
            return "Nenhum evento encontrado."
        resposta = "\n".join([
            f"\n📅 {ev.get('summary', 'Sem título')}\nInício: {ev['start'].get('dateTime')}\nFim: {ev['end'].get('dateTime')}\nID: {ev['id']}"
            for ev in eventos
        ])
        return resposta
    except Exception as e:
        return f"❌ Erro ao listar eventos: {str(e)}"

def buscar_horarios(inicio, fim, duracao):
    try:
        slots = cal.buscar_horarios_livres(inicio, fim, int(duracao))
        if not slots:
            return "Nenhum horário livre encontrado."
        return "\n".join([
            f"🔹 Início: {slot['inicio'].isoformat()} | Fim: {slot['fim'].isoformat()}"
            for slot in slots
        ])
    except Exception as e:
        return f"❌ Erro ao buscar horários: {str(e)}"

def atualizar_evento(evento_id, campo, novo_valor):
    try:
        if campo not in ["summary", "description", "location", "colorId"]:
            return "❌ Campo inválido. Use: summary, description, location ou colorId."
        atualizado = cal.atualizar_evento(evento_id, {campo: novo_valor})
        if atualizado:
            return "✅ Evento atualizado com sucesso."
        return "❌ Evento não encontrado ou erro na atualização."
    except Exception as e:
        return f"❌ Erro ao atualizar evento: {str(e)}"

def excluir_evento(evento_id):
    try:
        resultado = cal.excluir_evento(evento_id)
        if resultado:
            return "✅ Evento excluído com sucesso."
        return "❌ Evento não encontrado ou erro na exclusão."
    except Exception as e:
        print(f"Erro ao excluir evento: {e}")
        return "❌ Erro ao excluir evento."

with gr.Blocks(title="Gerenciador Google Calendar") as app:
    gr.Markdown("# 🗓️ Assistente de Tarefas com Google Calendar")

    with gr.Tab("Criar Evento"):
        with gr.Row():
            titulo = gr.Text(label="Título")
            inicio = gr.Text(label="Início (YYYY-MM-DDTHH:MM:SS)", placeholder="2025-06-02T10:00:00")
            fim = gr.Text(label="Fim (YYYY-MM-DDTHH:MM:SS)", placeholder="2025-06-02T11:00:00")
        descricao = gr.Text(label="Descrição")
        local = gr.Text(label="Local")
        cor = gr.Text(label="Cor (1-11 opcional)")
        botao_criar = gr.Button("Criar Evento")
        saida_criar = gr.Textbox(label="Resultado")

        botao_criar.click(fn=criar_evento, inputs=[titulo, inicio, fim, descricao, local, cor], outputs=saida_criar)

    with gr.Tab("Listar Eventos"):
        max_resultados = gr.Slider(1, 30, value=5, label="Quantidade")
        botao_listar = gr.Button("Listar")
        saida_listar = gr.Textbox(label="Eventos", lines=15)
        botao_listar.click(fn=listar_eventos, inputs=[max_resultados], outputs=[saida_listar])

    with gr.Tab("Buscar Horários Livres"):
        data_inicio = gr.Text(label="Início (YYYY-MM-DDTHH:MM:SSZ)")
        data_fim = gr.Text(label="Fim (YYYY-MM-DDTHH:MM:SSZ)")
        duracao = gr.Number(label="Duração mínima (min)", value=60)
        botao_buscar = gr.Button("Buscar")
        saida_busca = gr.Textbox(label="Horários livres", lines=10)
        botao_buscar.click(fn=buscar_horarios, inputs=[data_inicio, data_fim, duracao], outputs=[saida_busca])

    with gr.Tab("Atualizar Evento"):
        evento_id_upd = gr.Text(label="ID do Evento")
        campo = gr.Text(label="Campo (summary, description, location, colorId)")
        novo_valor = gr.Text(label="Novo Valor")
        botao_upd = gr.Button("Atualizar")
        saida_upd = gr.Textbox(label="Resultado")
        botao_upd.click(fn=atualizar_evento, inputs=[evento_id_upd, campo, novo_valor], outputs=[saida_upd])

    with gr.Tab("Excluir Evento"):
        evento_id_del = gr.Text(label="ID do Evento")
        botao_del = gr.Button("Excluir")
        saida_del = gr.Textbox(label="Resultado")
        botao_del.click(fn=excluir_evento, inputs=[evento_id_del], outputs=[saida_del])

if __name__ == "__main__":
    app.launch()
