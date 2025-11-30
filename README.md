🧠 Assistente Virtual Pessoal para Gerenciamento de Tarefas


Aplicação desktop desenvolvida em Python (Tkinter + ttkbootstrap) que permite gerenciar uma agenda simples de eventos, além de oferecer um bloco de notas integrado.
Ideal para estudos, apresentações acadêmicas e uso pessoal.


📌 Funcionalidades
🗂️ Gerenciamento de Eventos



➕ Criar novos eventos

✏️ Editar eventos existentes

❌ Deletar um evento específico

🗑️ Deletar todos os eventos de uma só vez

📋 Exibir lista completa de eventos cadastrados

✔ Validação automática de data e hora

📝 Registro automático de ações no arquivo notas.txt

📝 Bloco de Notas Integrado



Visualizar anotações já existentes

Criar novas anotações

Salvar alterações diretamente no arquivo notas.txt

Limpar o conteúdo do bloco de notas



🎨 Interface Moderna

Construída com ttkbootstrap, permitindo um visual moderno e profissional

Organização em abas (tabs):

Criar Evento

Gerenciar Eventos

Bloco de Notas



🛠️ Tecnologias Utilizadas

Python 3.10+

Tkinter

ttkbootstrap (tema moderno para Tkinter)



📁 Estrutura do Projeto
assistente_tarefas/
│
├── main.py           # Código principal da aplicação (interface + lógica)
├── notas.txt         # Arquivo de anotações gerado automaticamente
├── README.md         # Documentação do projeto
└── requirements.txt  # Dependências do projeto


▶️ Como Executar o Projeto
1️⃣ Instale as dependências

No terminal:

pip install ttkbootstrap

Ou, caso use o arquivo requirements.txt:

pip install -r requirements.txt


2️⃣ Execute o programa
python main.py


A interface será aberta imediatamente.



🗂️ Sobre o Arquivo notas.txt

Esse arquivo é criado automaticamente na primeira execução.

Ele armazena:

Registros de ações (adicionar, editar e remover eventos)

Todas as anotações escritas no bloco de notas

Você pode apagá-lo manualmente se quiser reiniciar tudo.



💡 Possíveis Melhorias Futuras

Salvamento permanente dos eventos (JSON ou SQLite)

Filtros por data

Notificações automáticas

Exportação da agenda


👩‍💻 Autora
Nome	   GitHub
Maria	   @mariastourna
