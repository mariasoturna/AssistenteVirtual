from utils.calendario.google import GerenciadorCalendarioGoogle
from commands.processador_linguagem import ProcessadorLinguagemNatural
from datetime import datetime, timedelta, date
import pytz
from tkinter import messagebox  # Para integração com a GUI
import re

class GerenciadorTarefas:
    def __init__(self):
        self.calendario = GerenciadorCalendarioGoogle()
        self.processador = ProcessadorLinguagemNatural()
        self.fuso_horario = pytz.timezone("America/Sao_Paulo")
        self.categorias_cores = {
            "trabalho": "11",  # Vermelho
            "pessoal": "9",    # Verde
            "estudo": "7",     # Azul
            "geral": "5"       # Amarelo
        }
        self.prioridades_prefixos = {
            "alta": "⚠️ ",
            "média": "⚡ ",
            "baixa": "🔹 ",
            "normal": ""
        }
        # Cache de eventos para evitar chamadas repetidas à API
        self.cache_eventos = {}
        self.cache_validade = None

    def executar_comando(self, comando):
        try:
            info_tarefa = self.processador.extrair_info_tarefa(comando)
            acao = info_tarefa["acao"]
            
            # Tratamento de diferentes tipos de ações
            if acao in ["adicionar", "lembrar"]:
                return self._criar_tarefa(info_tarefa)
            elif acao == "listar":
                return self._listar_tarefas(info_tarefa)
            elif acao == "atualizar":
                return self._atualizar_tarefa(info_tarefa)
            elif acao == "excluir":
                return self._excluir_tarefa(info_tarefa)
            elif acao == "reunir":
                return self._agendar_reuniao(info_tarefa)
            else:
                return f"Comando '{acao}' não reconhecido. Tente: 'Adicionar/Lembrar/Listar/Atualizar/Excluir [tarefa] [data] [hora]'"

        except Exception as e:
            return f"Erro ao processar comando: {str(e)}"

    def _criar_tarefa(self, info_tarefa):
        """Cria uma nova tarefa no calendário"""
        prazo = info_tarefa.get("prazo", "breve")
        hora = info_tarefa.get("hora", "")
        detalhes = info_tarefa.get("detalhes", "Tarefa sem descrição")
        categoria = info_tarefa.get("categoria", "geral")
        prioridade = info_tarefa.get("prioridade", "normal")
        local = info_tarefa.get("local", "")
        pessoas = info_tarefa.get("pessoas", [])

        # Formatação do título com prioridade
        titulo_formatado = f"{self.prioridades_prefixos[prioridade]}{detalhes}"
        
        # Descrição detalhada
        descricao = f"Prioridade: {prioridade.upper()}\n"
        if local:
            descricao += f"Local: {local}\n"
        if pessoas:
            descricao += f"Pessoas: {', '.join(pessoas)}\n"
        
        # Confirmação via GUI
        mensagem_confirmacao = (
            f"Criar tarefa:\n"
            f"• Título: {detalhes}\n"
            f"• Categoria: {categoria}\n"
            f"• Prioridade: {prioridade}\n"
            f"• Data: {prazo}\n"
            f"• Horário: {hora if hora else 'não especificado'}"
        )
        if local:
            mensagem_confirmacao += f"\n• Local: {local}"
        if pessoas:
            mensagem_confirmacao += f"\n• Pessoas: {', '.join(pessoas)}"
            
        confirmacao = messagebox.askyesno("Confirmar", mensagem_confirmacao)

        if not confirmacao:
            return "Operação cancelada pelo usuário."

        # Processamento de data e hora
        data_hora_inicio, data_hora_fim = self._processar_data_hora(prazo, hora)
        
        # Adicionar evento ao calendário com cor baseada na categoria
        cor_evento = self.categorias_cores.get(categoria, "5")  # Padrão: amarelo
        
        evento_id = self.calendario.adicionar_evento(
            titulo=titulo_formatado,
            inicio=data_hora_inicio.isoformat(),
            fim=data_hora_fim.isoformat(),
            descricao=descricao,
            local=local,
            cor=cor_evento
        )
        
        # Invalidar cache após modificação
        self.cache_validade = None

        return (
            f"✅ Tarefa criada com sucesso:\n"
            f"• Título: {detalhes}\n"
            f"• Categoria: {categoria}\n"
            f"• Prioridade: {prioridade}\n"
            f"• Data: {prazo}\n"
            f"• Horário: {hora if hora else 'não especificado'}"
        )

    def _listar_tarefas(self, info_tarefa):
        """Lista tarefas do calendário com filtros opcionais"""
        # Extrair filtros da informação da tarefa
        filtro_categoria = info_tarefa.get("categoria", None)
        filtro_prioridade = info_tarefa.get("prioridade", None)
        filtro_data = info_tarefa.get("prazo", None)
        
        # Verificar se o cache é válido (24 horas)
        agora = datetime.now(self.fuso_horario)
        if not self.cache_validade or (agora - self.cache_validade).total_seconds() > 86400:
            # Buscar eventos dos próximos 30 dias
            inicio = agora.isoformat()
            fim = (agora + timedelta(days=30)).isoformat()
            eventos = self.calendario.listar_eventos(inicio, fim)
            
            # Atualizar cache
            self.cache_eventos = eventos
            self.cache_validade = agora
        else:
            eventos = self.cache_eventos
        
        # Aplicar filtros
        eventos_filtrados = []
        for evento in eventos:
            # Extrair informações do evento
            titulo = evento.get('summary', '')
            data_inicio = datetime.fromisoformat(evento.get('start', {}).get('dateTime', ''))
            
            # Verificar categoria pelo código de cor
            cor_evento = evento.get('colorId', '5')
            categoria_evento = next((cat for cat, cor in self.categorias_cores.items() if cor == cor_evento), "geral")
            
            # Verificar prioridade pelo prefixo no título
            prioridade_evento = "normal"
            for prio, prefixo in self.prioridades_prefixos.items():
                if prefixo and titulo.startswith(prefixo):
                    prioridade_evento = prio
                    break
            
            # Aplicar filtros
            if filtro_categoria and categoria_evento != filtro_categoria:
                continue
            if filtro_prioridade and prioridade_evento != filtro_prioridade:
                continue
            if filtro_data:
                # Comparar apenas a data, ignorando a hora
                data_evento = data_inicio.date()
                # Converter filtro_data para objeto date se for string
                if isinstance(filtro_data, str):
                    # Tentar diferentes formatos de data
                    try:
                        # Formato DD/MM/YYYY
                        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', filtro_data):
                            partes = filtro_data.split('/')
                            data_filtro = date(int(partes[2]), int(partes[1]), int(partes[0]))
                        # Formato YYYY-MM-DD
                        elif re.match(r'\d{4}-\d{1,2}-\d{1,2}', filtro_data):
                            data_filtro = date.fromisoformat(filtro_data)
                        else:
                            # Se não conseguir converter, pular filtro de data
                            data_filtro = None
                    except:
                        data_filtro = None
                    
                    if data_filtro and data_evento != data_filtro:
                        continue
            
            # Se passou por todos os filtros, adicionar à lista
            eventos_filtrados.append({
                'titulo': titulo,
                'data_inicio': data_inicio.strftime('%d/%m/%Y %H:%M'),
                'categoria': categoria_evento,
                'prioridade': prioridade_evento,
                'id': evento.get('id', '')
            })
        
        # Ordenar por data
        eventos_filtrados.sort(key=lambda x: x['data_inicio'])
        
        # Formatar resultado
        if not eventos_filtrados:
            return "Nenhuma tarefa encontrada com os filtros especificados."
        
        resultado = "📋 Tarefas encontradas:\n\n"
        for i, evento in enumerate(eventos_filtrados, 1):
            # Remover prefixo de prioridade do título para exibição
            titulo_limpo = evento['titulo']
            for prefixo in self.prioridades_prefixos.values():
                if prefixo and titulo_limpo.startswith(prefixo):
                    titulo_limpo = titulo_limpo[len(prefixo):]
            
            resultado += (
                f"{i}. {titulo_limpo}\n"
                f"   • Data/Hora: {evento['data_inicio']}\n"
                f"   • Categoria: {evento['categoria']}\n"
                f"   • Prioridade: {evento['prioridade']}\n"
                f"   • ID: {evento['id']}\n\n"
            )
        
        return resultado

    def _atualizar_tarefa(self, info_tarefa):
        """Atualiza uma tarefa existente no calendário"""
        evento_id = info_tarefa.get("id", "")
        if not evento_id:
            return "É necessário fornecer o ID da tarefa para atualizá-la. Use o comando 'listar' para ver os IDs."
        
        # Buscar evento atual
        evento_atual = self.calendario.obter_evento(evento_id)
        if not evento_atual:
            return f"Tarefa com ID {evento_id} não encontrada."
        
        # Preparar dados para atualização
        titulo_atual = evento_atual.get('summary', '')
        descricao_atual = evento_atual.get('description', '')
        local_atual = evento_atual.get('location', '')
        
        # Extrair prioridade atual do título
        prioridade_atual = "normal"
        for prio, prefixo in self.prioridades_prefixos.items():
            if prefixo and titulo_atual.startswith(prefixo):
                prioridade_atual = prio
                titulo_atual = titulo_atual[len(prefixo):]
                break
        
        # Extrair categoria atual pela cor
        cor_atual = evento_atual.get('colorId', '5')
        categoria_atual = next((cat for cat, cor in self.categorias_cores.items() if cor == cor_atual), "geral")
        
        # Aplicar atualizações
        detalhes = info_tarefa.get("detalhes")
        categoria = info_tarefa.get("categoria", categoria_atual)
        prioridade = info_tarefa.get("prioridade", prioridade_atual)
        prazo = info_tarefa.get("prazo")
        hora = info_tarefa.get("hora")
        local = info_tarefa.get("local", local_atual)
        
        # Preparar título com prioridade
        if detalhes:
            titulo_novo = detalhes
        else:
            titulo_novo = titulo_atual
            
        titulo_formatado = f"{self.prioridades_prefixos[prioridade]}{titulo_novo}"
        
        # Atualizar descrição
        descricao_nova = f"Prioridade: {prioridade.upper()}\n"
        if local:
            descricao_nova += f"Local: {local}\n"
        
        # Processar data e hora se fornecidos
        data_hora_inicio = None
        data_hora_fim = None
        if prazo or hora:
            data_hora_inicio, data_hora_fim = self._processar_data_hora(
                prazo or evento_atual.get('start', {}).get('dateTime', ''),
                hora or ""
            )
        
        # Confirmação via GUI
        mensagem_confirmacao = "Atualizar tarefa:\n"
        if detalhes:
            mensagem_confirmacao += f"• Título: {titulo_atual} → {detalhes}\n"
        if categoria != categoria_atual:
            mensagem_confirmacao += f"• Categoria: {categoria_atual} → {categoria}\n"
        if prioridade != prioridade_atual:
            mensagem_confirmacao += f"• Prioridade: {prioridade_atual} → {prioridade}\n"
        if prazo:
            mensagem_confirmacao += f"• Data: {prazo}\n"
        if hora:
            mensagem_confirmacao += f"• Horário: {hora}\n"
        if local != local_atual:
            mensagem_confirmacao += f"• Local: {local_atual} → {local}\n"
            
        confirmacao = messagebox.askyesno("Confirmar Atualização", mensagem_confirmacao)
        if not confirmacao:
            return "Operação cancelada pelo usuário."
        
        # Preparar dados para atualização
        dados_atualizacao = {
            'summary': titulo_formatado,
            'description': descricao_nova,
            'colorId': self.categorias_cores.get(categoria, '5')
        }
        
        if local:
            dados_atualizacao['location'] = local
            
        if data_hora_inicio and data_hora_fim:
            dados_atualizacao['start'] = {'dateTime': data_hora_inicio.isoformat()}
            dados_atualizacao['end'] = {'dateTime': data_hora_fim.isoformat()}
        
        # Atualizar evento
        self.calendario.atualizar_evento(evento_id, dados_atualizacao)
        
        # Invalidar cache após modificação
        self.cache_validade = None
        
        return "✅ Tarefa atualizada com sucesso!"

    def _excluir_tarefa(self, info_tarefa):
        """Exclui uma tarefa do calendário"""
        evento_id = info_tarefa.get("id", "")
        if not evento_id:
            return "É necessário fornecer o ID da tarefa para excluí-la. Use o comando 'listar' para ver os IDs."
        
        # Buscar evento para confirmação
        evento = self.calendario.obter_evento(evento_id)
        if not evento:
            return f"Tarefa com ID {evento_id} não encontrada."
        
        titulo = evento.get('summary', 'Sem título')
        
        # Confirmação via GUI
        confirmacao = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a tarefa:\n{titulo}?"
        )
        
        if not confirmacao:
            return "Operação cancelada pelo usuário."
        
        # Excluir evento
        self.calendario.excluir_evento(evento_id)
        
        # Invalidar cache após modificação
        self.cache_validade = None
        
        return "✅ Tarefa excluída com sucesso!"

    def _agendar_reuniao(self, info_tarefa):
        """Agenda uma reunião com verificação de disponibilidade"""
        detalhes = info_tarefa.get("detalhes", "Reunião")
        prazo = info_tarefa.get("prazo", "breve")
        hora = info_tarefa.get("hora", "")
        local = info_tarefa.get("local", "")
        pessoas = info_tarefa.get("pessoas", [])
        duracao = info_tarefa.get("duracao", 60)  # Duração em minutos
        
        # Processar data e hora
        data_hora_inicio, data_hora_fim = self._processar_data_hora(prazo, hora, duracao)
        
        # Verificar disponibilidade
        disponibilidade = self._verificar_disponibilidade(data_hora_inicio, data_hora_fim)
        
        if not disponibilidade['disponivel']:
            # Sugerir horários alternativos
            sugestoes = self._sugerir_horarios_alternativos(data_hora_inicio.date(), duracao, 3)
            
            mensagem = (
                f"⚠️ Conflito detectado com o evento: {disponibilidade['evento_conflito']}\n\n"
                f"Horários alternativos sugeridos:\n"
            )
            
            for i, sugestao in enumerate(sugestoes, 1):
                mensagem += f"{i}. {sugestao['inicio'].strftime('%d/%m/%Y %H:%M')} - {sugestao['fim'].strftime('%H:%M')}\n"
            
            return mensagem
        
        # Confirmação via GUI
        mensagem_confirmacao = (
            f"Agendar reunião:\n"
            f"• Título: {detalhes}\n"
            f"• Data: {data_hora_inicio.strftime('%d/%m/%Y')}\n"
            f"• Horário: {data_hora_inicio.strftime('%H:%M')} - {data_hora_fim.strftime('%H:%M')}"
        )
        
        if local:
            mensagem_confirmacao += f"\n• Local: {local}"
        if pessoas:
            mensagem_confirmacao += f"\n• Participantes: {', '.join(pessoas)}"
            
        confirmacao = messagebox.askyesno("Confirmar Reunião", mensagem_confirmacao)
        
        if not confirmacao:
            return "Operação cancelada pelo usuário."
        
        # Adicionar evento de reunião ao calendário
        evento_id = self.calendario.adicionar_evento(
            titulo=f"📅 {detalhes}",
            inicio=data_hora_inicio.isoformat(),
            fim=data_hora_fim.isoformat(),
            descricao=f"Reunião agendada via Assistente Virtual\nParticipantes: {', '.join(pessoas)}",
            local=local,
            cor="11"  # Vermelho para reuniões
        )
        
        # Invalidar cache após modificação
        self.cache_validade = None
        
        return (
            f"✅ Reunião agendada com sucesso:\n"
            f"• Título: {detalhes}\n"
            f"• Data: {data_hora_inicio.strftime('%d/%m/%Y')}\n"
            f"• Horário: {data_hora_inicio.strftime('%H:%M')} - {data_hora_fim.strftime('%H:%M')}\n"
            f"• Local: {local if local else 'Não especificado'}\n"
            f"• Participantes: {', '.join(pessoas) if pessoas else 'Não especificados'}"
        )

    def _processar_data_hora(self, prazo, hora, duracao_minutos=60):
        """Processa strings de data e hora para objetos datetime"""
        agora = datetime.now(self.fuso_horario)
        
        # Processar data
        if prazo == "breve" or not prazo:
            # Se não houver data específica, usar o dia seguinte
            data = agora.date() + timedelta(days=1)
        elif prazo == "hoje":
            data = agora.date()
        elif prazo == "amanhã":
            data = agora.date() + timedelta(days=1)
        elif prazo == "depois de amanhã":
            data = agora.date() + timedelta(days=2)
        elif prazo == "próxima semana":
            # Próxima segunda-feira
            dias_ate_segunda = 7 - agora.weekday()
            data = agora.date() + timedelta(days=dias_ate_segunda)
        elif prazo == "próximo mês":
            # Primeiro dia do próximo mês
            if agora.month == 12:
                data = date(agora.year + 1, 1, 1)
            else:
                data = date(agora.year, agora.month + 1, 1)
        else:
            # Tentar interpretar formatos comuns de data
            try:
                # Formato DD/MM/YYYY
                if re.match(r'\d{1,2}/\d{1,2}/\d{4}', prazo):
                    partes = prazo.split('/')
                    data = date(int(partes[2]), int(partes[1]), int(partes[0]))
                # Formato YYYY-MM-DD
                elif re.match(r'\d{4}-\d{1,2}-\d{1,2}', prazo):
                    data = date.fromisoformat(prazo)
                else:
                    # Se não conseguir interpretar, usar amanhã
                    data = agora.date() + timedelta(days=1)
            except:
                # Em caso de erro, usar amanhã
                data = agora.date() + timedelta(days=1)
        
        # Processar hora
        if not hora:
            # Se não houver hora específica, usar 9:00
            hora_inicio = datetime.combine(data, datetime.min.time().replace(hour=9, minute=0))
        else:
            # Tentar interpretar formatos comuns de hora
            try:
                # Formato HH:MM
                if re.match(r'\d{1,2}:\d{2}', hora):
                    partes = hora.split(':')
                    hora_inicio = datetime.combine(
                        data, 
                        datetime.min.time().replace(hour=int(partes[0]), minute=int(partes[1]))
                    )
                # Formato HHh ou HHhMM
                elif re.match(r'\d{1,2}h(\d{2})?', hora):
                    if 'h' in hora and not hora.endswith('h'):
                        partes = hora.split('h')
                        hora_inicio = datetime.combine(
                            data, 
                            datetime.min.time().replace(hour=int(partes[0]), minute=int(partes[1]))
                        )
                    else:
                        hora_inicio = datetime.combine(
                            data, 
                            datetime.min.time().replace(hour=int(hora.replace('h', '')), minute=0)
                        )
                else:
                    # Se não conseguir interpretar, usar 9:00
                    hora_inicio = datetime.combine(data, datetime.min.time().replace(hour=9, minute=0))
            except:
                # Em caso de erro, usar 9:00
                hora_inicio = datetime.combine(data, datetime.min.time().replace(hour=9, minute=0))
        
        # Adicionar fuso horário
        hora_inicio = self.fuso_horario.localize(hora_inicio)
        
        # Calcular hora de término (duração padrão: 1 hora)
        hora_fim = hora_inicio + timedelta(minutes=duracao_minutos)
        
        return hora_inicio, hora_fim

    def _verificar_disponibilidade(self, inicio, fim):
        """Verifica se há conflitos de agenda no período especificado"""
        # Buscar eventos no período
        eventos = self.calendario.listar_eventos(inicio.isoformat(), fim.isoformat())
        
        if eventos:
            # Há conflito
            return {
                'disponivel': False,
                'evento_conflito': eventos[0].get('summary', 'Evento sem título')
            }
        
        # Não há conflito
        return {'disponivel': True}

    def _sugerir_horarios_alternativos(self, data, duracao_minutos=60, quantidade=3):
        """Sugere horários alternativos disponíveis na data especificada"""
        # Horários de trabalho padrão (8h às 18h)
        hora_inicio_dia = 8
        hora_fim_dia = 18
        
        # Buscar todos os eventos do dia
        inicio_dia = datetime.combine(data, datetime.min.time().replace(hour=hora_inicio_dia))
        inicio_dia = self.fuso_horario.localize(inicio_dia)
        
        fim_dia = datetime.combine(data, datetime.min.time().replace(hour=hora_fim_dia))
        fim_dia = self.fuso_horario.localize(fim_dia)
        
        eventos_dia = self.calendario.listar_eventos(inicio_dia.isoformat(), fim_dia.isoformat())
        
        # Converter eventos para períodos ocupados
        periodos_ocupados = []
        for evento in eventos_dia:
            inicio_evento = datetime.fromisoformat(evento.get('start', {}).get('dateTime', ''))
            fim_evento = datetime.fromisoformat(evento.get('end', {}).get('dateTime', ''))
            periodos_ocupados.append((inicio_evento, fim_evento))
        
        # Ordenar períodos ocupados
        periodos_ocupados.sort(key=lambda x: x[0])
        
        # Encontrar espaços livres
        horarios_livres = []
        hora_atual = inicio_dia
        
        for inicio_ocupado, fim_ocupado in periodos_ocupados:
            # Verificar se há espaço antes do próximo evento
            if (inicio_ocupado - hora_atual).total_seconds() >= duracao_minutos * 60:
                # Há espaço suficiente
                horarios_livres.append({
                    'inicio': hora_atual,
                    'fim': hora_atual + timedelta(minutes=duracao_minutos)
                })
            
            # Avançar para depois do evento ocupado
            hora_atual = max(hora_atual, fim_ocupado)
        
        # Verificar se há espaço após o último evento
        if (fim_dia - hora_atual).total_seconds() >= duracao_minutos * 60:
            horarios_livres.append({
                'inicio': hora_atual,
                'fim': hora_atual + timedelta(minutes=duracao_minutos)
            })
        
        # Limitar à quantidade solicitada
        return horarios_livres[:quantidade]