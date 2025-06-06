# gerenciador.py

class GerenciadorTarefas:
    def __init__(self):
        self.tarefas = {}

    def adicionar_tarefa(self, data, descricao):
        if data not in self.tarefas:
            self.tarefas[data] = []
        self.tarefas[data].append(descricao)
        return f"Tarefa adicionada em {data}."

    def listar_tarefas(self, data):
        if data in self.tarefas:
            return f"Tarefas em {data}:\n" + "\n".join(f"- {t}" for t in self.tarefas[data])
        return f"Não há tarefas para {data}."

    def remover_tarefa(self, data, descricao):
        if data in self.tarefas and descricao in self.tarefas[data]:
            self.tarefas[data].remove(descricao)
            return f"Tarefa removida de {data}."
        return "Tarefa não encontrada."

    def limpar_tudo(self):
        self.tarefas.clear()
        return "Todas as tarefas foram apagadas."
