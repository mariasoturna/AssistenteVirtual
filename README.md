
# 🧠 Assistente Virtual Pessoal para Gerenciamento de Tarefas

Este projeto é um **assistente virtual pessoal** desenvolvido em Python, com interface web via **Gradio**, que permite aos usuários **gerenciar uma agenda de tarefas simulada**, incluindo criação, listagem, atualização e remoção de compromissos.

---

## 📌 Funcionalidades

- ✅ Criar novos compromissos
- 📅 Listar eventos do dia atual
- ✏️ Atualizar eventos existentes
- ❌ Remover eventos por título ou data
- 💬 Interface interativa com linguagem natural
- 🌐 Acesso fácil via navegador com deploy no Render

---

## 🛠 Tecnologias Utilizadas

- **Python 3.10+**
- **Gradio 4.32.1**
- Hospedagem: [Render](https://render.com/)

---

## 📁 Estrutura do Projeto

```
meu_assistente_virtual/
│
├── app.py               # Arquivo principal com a interface Gradio
├── agenda_simulada.py   # Simulação das funcionalidades de agenda
├── requirements.txt     # Dependência do projeto
├── render.yaml          # Configuração do deploy na Render
└── README.md            # Documentação do projeto
```

---

## ▶️ Como Executar Localmente

1. **Clone o repositório:**

```bash
git clone https://github.com/mariastourna/AssistenteVirtual.git
cd AssistenteVirtual
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute o aplicativo:**

```bash
python app.py
```

O Gradio abrirá automaticamente no navegador ou informará uma URL local para acesso.

---

## 🌐 Deploy Online

O projeto pode ser acessado facilmente através do Render após configuração do repositório e deploy. O serviço usa `render.yaml` para automatizar o processo de build e execução.

---

## 📅 Simulação de Agenda

Todos os dados são armazenados em memória (não há banco de dados), simulando uma agenda simples. Ideal para apresentações ou testes de funcionalidades.

---

## ✨ Demonstração

[🔗 Link para o app no Render](https://seu-link-do-render.onrender.com)

---

## 👩‍💻 Autora

| Nome | GitHub |
|------|--------|
| Maria | [@mariastourna](https://github.com/mariastourna) |
