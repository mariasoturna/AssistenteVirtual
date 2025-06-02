from commands.processador_linguagem import ProcessadorLinguagemNatural

print("\n=== TESTE DO PROCESSADOR ===")
testes = [
    "Lembrar comprar leite amanhã às 10",
    "Adicionar reunião com cliente sexta-feira 15h",
    "Marcar consulta médica dia 20/08 às 9:30"
]

processador = ProcessadorLinguagemNatural()
for comando in testes:
    print(f"\nComando: '{comando}'")
    print(processador.extrair_info_tarefa(comando))