import gradio as gr
import os

NOTAS_ARQUIVO = "notas.txt"

def salvar_notas(texto):
    with open(NOTAS_ARQUIVO, "w", encoding="utf-8") as f:
        f.write(texto)
    return "Notas salvas com sucesso!"

def carregar_notas():
    if not os.path.exists(NOTAS_ARQUIVO):
        return ""
    with open(NOTAS_ARQUIVO, "r", encoding="utf-8") as f:
        return f.read()

def limpar_notas():
    return ""

def interface():
    with gr.Blocks(title="Assistente Virtual") as demo:

        gr.Markdown("## Assistente Virtual — Gerenciamento de Tarefas")

        # --- Botão para abrir o Bloco de Notas ---
        with gr.Row():
            botao_bloconotas = gr.Button("📝 Bloco de Notas", size="lg")

        # --- Modal do bloco de notas ---
        with gr.Dialog(title="Bloco de Notas") as modal_notas:
            notas = gr.Textbox(label="Escreva suas notas aqui:", lines=15)

            with gr.Row():
                btn_salvar = gr.Button("💾 Salvar")
                btn_carregar = gr.Button("📂 Carregar")
                btn_limpar = gr.Button("🧼 Limpar")

            status = gr.Markdown("")

        # Eventos
        botao_bloconotas.click(lambda: gr.show(), None, modal_notas)

        btn_salvar.click(salvar_notas, notas, status)
        btn_carregar.click(lambda: carregar_notas(), None, notas)
        btn_limpar.click(lambda: "", None, notas)

    return demo


if __name__ == "__main__":
    interface().launch()