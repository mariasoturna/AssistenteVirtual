import spacy
import re
from datetime import datetime, timedelta

class ProcessadorLinguagemNatural:
    def __init__(self, modelo='pt_core_news_sm'):
        self.nlp = spacy.load(modelo)
        # Palavras-chave para categorização
        self.categorias = {
            'trabalho': ['trabalho', 'reunião', 'projeto', 'cliente', 'relatório', 'apresentação', 'email', 'e-mail', 'profissional', 'escritório', 'negócio'],
            'pessoal': ['casa', 'família', 'amigo', 'lazer', 'hobby', 'compras', 'médico', 'saúde', 'pessoal', 'aniversário', 'festa'],
            'estudo': ['estudar', 'aula', 'curso', 'faculdade', 'leitura', 'livro', 'prova', 'exercício', 'escola', 'universidade', 'aprender']
        }
        # Palavras-chave para prioridade
        self.prioridades = {
            'alta': ['urgente', 'importante', 'crítico', 'prioritário', 'essencial', 'imediato', 'emergência', 'crucial'],
            'média': ['relevante', 'significativo', 'considerável', 'moderado', 'médio', 'intermediário'],
            'baixa': ['eventual', 'quando possível', 'se der tempo', 'opcional', 'baixa prioridade', 'secundário']
        }
        # Expressões de tempo relativas
        self.expressoes_tempo = {
            'hoje': 0,
            'amanhã': 1,
            'depois de amanhã': 2,
            'próxima semana': 7,
            'próximo mês': 30
        }

    def extrair_info_tarefa(self, texto):
        texto_original = texto.lower()
        doc = self.nlp(texto_original)

        # Extrai entidades (data/hora)
        prazo = None
        hora = None
        local = None
        pessoas = []

        # Processamento de entidades nomeadas
        for ent in doc.ents:
            if ent.label_ == "DATE":
                prazo = self._processar_data(ent.text)
            elif ent.label_ == "TIME":
                hora = self._processar_hora(ent.text)
            elif ent.label_ == "LOC" or ent.label_ == "GPE":
                local = ent.text
            elif ent.label_ == "PERSON":
                pessoas.append(ent.text)

        # Limpeza do texto (remove palavras-chave)
        texto_limpo = texto_original
        palavras_remover = ["adicionar", "lembrar", "criar", "marcar", "por favor", "agendar", "reunião", "reunir"]
        if prazo:
            # Remover apenas a expressão exata de data, não partes de outras palavras
            texto_limpo = re.sub(r'\b' + re.escape(prazo) + r'\b', '', texto_limpo)
        if hora:
            # Remover apenas a expressão exata de hora, não partes de outras palavras
            texto_limpo = re.sub(r'\b' + re.escape(hora) + r'\b', '', texto_limpo)
        if local:
            texto_limpo = re.sub(r'\b' + re.escape(local) + r'\b', '', texto_limpo)
        for pessoa in pessoas:
            texto_limpo = re.sub(r'\b' + re.escape(pessoa) + r'\b', '', texto_limpo)

        for palavra in palavras_remover:
            texto_limpo = re.sub(r'\b' + re.escape(palavra) + r'\b', '', texto_limpo)
            
        texto_limpo = " ".join(texto_limpo.split()).strip()

        # Determinar categoria da tarefa
        categoria = self._determinar_categoria(texto_original)
        
        # Determinar prioridade da tarefa
        prioridade = self._determinar_prioridade(texto_original)
        
        # Análise de sentimento básica
        sentimento = self._analisar_sentimento(doc)

        # Retorno padronizado e expandido
        return {
            "acao": self._determinar_acao(texto_original),
            "prazo": prazo or "breve",
            "hora": hora or "",
            "local": local or "",
            "pessoas": pessoas,
            "categoria": categoria,
            "prioridade": prioridade,
            "sentimento": sentimento,
            "detalhes": texto_limpo if texto_limpo else "Tarefa sem descrição",
            "texto_original": texto_original
        }
    
    def _processar_data(self, texto_data):
        """Processa expressões de data, incluindo relativas como 'amanhã'"""
        texto_data = texto_data.lower()
        
        # Adicionar mais expressões relativas
        expressoes_adicionais = {
            'depois de amanhã': 2,
            'próxima segunda': self._dias_ate_proximo_dia_semana(0),
            'próxima terça': self._dias_ate_proximo_dia_semana(1),
            'próxima quarta': self._dias_ate_proximo_dia_semana(2),
            'próxima quinta': self._dias_ate_proximo_dia_semana(3),
            'próxima sexta': self._dias_ate_proximo_dia_semana(4),
            'próximo sábado': self._dias_ate_proximo_dia_semana(5),
            'próximo domingo': self._dias_ate_proximo_dia_semana(6),
            'fim de semana': self._dias_ate_proximo_dia_semana(5),  # Próximo sábado
            'fim do mês': self._dias_ate_fim_do_mes(),
            'início do próximo mês': self._dias_ate_inicio_proximo_mes()
        }
        
        # Combinar com expressões existentes
        todas_expressoes = {**self.expressoes_tempo, **expressoes_adicionais}
        
        # Verificar expressões relativas
        for expressao, dias in todas_expressoes.items():
            if expressao in texto_data:
                data_futura = datetime.now() + timedelta(days=dias)
                return data_futura.strftime("%d/%m/%Y")
        
        # Tentar extrair data no formato DD/MM ou DD/MM/AAAA
        match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', texto_data)
        if match:
            dia = int(match.group(1))
            mes = int(match.group(2))
            ano = int(match.group(3)) if match.group(3) else datetime.now().year
            
            # Ajustar ano de dois dígitos
            if ano < 100:
                ano += 2000
                
            try:
                return datetime(ano, mes, dia).strftime("%d/%m/%Y")
            except ValueError:
                pass
        
        # Verificar expressões como "dia 10"
        match = re.search(r'dia (\d{1,2})', texto_data)
        if match:
            dia = int(match.group(1))
            hoje = datetime.now()
            
            # Se o dia já passou neste mês, considerar o próximo mês
            if dia < hoje.day:
                proximo_mes = hoje.month + 1
                ano = hoje.year
                if proximo_mes > 12:
                    proximo_mes = 1
                    ano += 1
                try:
                    return datetime(ano, proximo_mes, dia).strftime("%d/%m/%Y")
                except ValueError:
                    pass
            else:
                try:
                    return datetime(hoje.year, hoje.month, dia).strftime("%d/%m/%Y")
                except ValueError:
                    pass
        
        # Se não for expressão relativa, retorna o texto original
        return texto_data
    
    def _dias_ate_proximo_dia_semana(self, dia_alvo):
        """Calcula dias até o próximo dia da semana específico (0=segunda, 6=domingo)"""
        hoje = datetime.now().weekday()
        dias = (dia_alvo - hoje) % 7
        if dias == 0:  # Se for o mesmo dia da semana, vai para a próxima semana
            dias = 7
        return dias

    def _dias_ate_fim_do_mes(self):
        """Calcula dias até o fim do mês atual"""
        hoje = datetime.now()
        ultimo_dia = (hoje.replace(month=hoje.month % 12 + 1, day=1) - timedelta(days=1)).day
        return ultimo_dia - hoje.day

    def _dias_ate_inicio_proximo_mes(self):
        """Calcula dias até o início do próximo mês"""
        hoje = datetime.now()
        proximo_mes = hoje.replace(month=hoje.month % 12 + 1, day=1)
        return (proximo_mes - hoje.replace(hour=0, minute=0, second=0, microsecond=0)).days
    
    def _processar_hora(self, texto_hora):
        """Processa diferentes formatos de hora"""
        texto_hora = texto_hora.lower().replace("às", "").strip()
        
        # Formato "14h30" ou "14h"
        if "h" in texto_hora:
            if ":" not in texto_hora:
                partes = texto_hora.split("h")
                if len(partes) == 2 and partes[0].isdigit():
                    if partes[1] and partes[1].isdigit():
                        return f"{int(partes[0]):02d}:{partes[1]}"
                    else:
                        return f"{int(partes[0]):02d}:00"
        
        # Formato "14:30"
        if re.match(r'^\d{1,2}:\d{2}$', texto_hora):
            partes = texto_hora.split(":")
            return f"{int(partes[0]):02d}:{partes[1]}"
        
        # Formato "da tarde", "da noite"
        if "da tarde" in texto_hora:
            texto_hora = texto_hora.replace("da tarde", "").strip()
            # Extrair número da hora
            match = re.search(r'(\d+)(?::(\d+))?', texto_hora)
            if match:
                hora = int(match.group(1))
                minuto = match.group(2) or "00"
                if hora < 12:  # Converter para formato 24h
                    hora += 12
                return f"{hora:02d}:{minuto}"
        
        if "da noite" in texto_hora:
            texto_hora = texto_hora.replace("da noite", "").strip()
            # Extrair número da hora
            match = re.search(r'(\d+)(?::(\d+))?', texto_hora)
            if match:
                hora = int(match.group(1))
                minuto = match.group(2) or "00"
                if hora < 12:  # Converter para formato 24h
                    hora += 12
                return f"{hora:02d}:{minuto}"
        
        if "da manhã" in texto_hora:
            texto_hora = texto_hora.replace("da manhã", "").strip()
            # Extrair número da hora
            match = re.search(r'(\d+)(?::(\d+))?', texto_hora)
            if match:
                hora = int(match.group(1))
                minuto = match.group(2) or "00"
                return f"{hora:02d}:{minuto}"
        
        # Se não conseguir processar, retorna o texto original
        return texto_hora
    
    def _determinar_acao(self, texto):
        """Determina a ação baseada no texto"""
        texto_lower = texto.lower()
        
        # Expandir reconhecimento de ações
        if any(palavra in texto_lower for palavra in ["lembrar", "lembre", "lembrete"]):
            return "lembrar"
        elif any(palavra in texto_lower for palavra in ["reunião", "reunir", "agendar reunião", "marcar reunião"]):
            return "reunir"
        elif any(palavra in texto_lower for palavra in ["ligar", "telefonar", "chamar", "contatar"]):
            return "ligar"
        elif any(palavra in texto_lower for palavra in ["email", "e-mail", "enviar email", "mandar email"]):
            return "email"
        elif any(palavra in texto_lower for palavra in ["adicionar", "criar", "nova tarefa", "incluir"]):
            return "adicionar"
        else:
            # Padrão para comandos não específicos
            return "adicionar"
    
    def _determinar_categoria(self, texto):
        """Determina a categoria da tarefa baseada em palavras-chave"""
        texto_lower = texto.lower()
        
        # Verificar menções explícitas de categoria
        match = re.search(r'categoria:(\w+)', texto_lower)
        if match:
            categoria = match.group(1)
            if categoria in ['trabalho', 'pessoal', 'estudo', 'geral']:
                return categoria
        
        # Verificar palavras-chave
        pontuacao = {'trabalho': 0, 'pessoal': 0, 'estudo': 0}
        
        for categoria, palavras in self.categorias.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    pontuacao[categoria] += 1
        
        # Determinar categoria com maior pontuação
        categoria_max = max(pontuacao.items(), key=lambda x: x[1])
        
        # Se não houver palavras-chave, retornar "geral"
        if categoria_max[1] == 0:
            return "geral"
        
        return categoria_max[0]
    
    def _determinar_prioridade(self, texto):
        """Determina a prioridade da tarefa baseada em palavras-chave"""
        texto_lower = texto.lower()
        
        # Verificar menções explícitas de prioridade
        match = re.search(r'prioridade:(\w+)', texto_lower)
        if match:
            prioridade = match.group(1)
            if prioridade in ['alta', 'média', 'baixa', 'normal']:
                return prioridade
        
        # Verificar palavras-chave
        for prioridade, palavras in self.prioridades.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    return prioridade
        
        return "normal"
    
    def _analisar_sentimento(self, doc):
        """Análise mais sofisticada de sentimento"""
        # Palavras com pesos
        palavras_positivas = {
            "bom": 1, "ótimo": 2, "excelente": 2, "feliz": 1, 
            "animado": 1, "interessante": 1, "importante": 1,
            "urgente": 2, "prioritário": 2, "essencial": 2
        }
        
        palavras_negativas = {
            "ruim": -1, "péssimo": -2, "triste": -1, "chato": -1, 
            "difícil": -1, "complicado": -1, "atrasar": -2,
            "cancelar": -2, "adiar": -1, "problema": -1
        }
        
        # Modificadores de intensidade
        intensificadores = {
            "muito": 2, "extremamente": 3, "super": 2, "bastante": 1.5,
            "pouco": 0.5, "levemente": 0.7, "um pouco": 0.5
        }
        
        pontuacao = 0
        intensidade = 1
        
        # Analisar tokens
        for i, token in enumerate(doc):
            # Verificar se há intensificador antes
            if i > 0 and doc[i-1].text.lower() in intensificadores:
                intensidade = intensificadores[doc[i-1].text.lower()]
            
            # Calcular pontuação
            if token.text.lower() in palavras_positivas:
                pontuacao += palavras_positivas[token.text.lower()] * intensidade
            elif token.text.lower() in palavras_negativas:
                pontuacao += palavras_negativas[token.text.lower()] * intensidade
            
            # Resetar intensidade
            intensidade = 1
        
        # Determinar sentimento
        if pontuacao > 2:
            return "muito positivo"
        elif pontuacao > 0:
            return "positivo"
        elif pontuacao < -2:
            return "muito negativo"
        elif pontuacao < 0:
            return "negativo"
        else:
            return "neutro"