from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pytz
import os
import pickle

class GerenciadorCalendarioGoogle:
    def __init__(self, token_path='token.pickle', credentials_path='credentials.json'):
        """
        Inicializa o gerenciador de calendário com autenticação persistente.
        
        Args:
            token_path: Caminho para o arquivo de token salvo
            credentials_path: Caminho para o arquivo de credenciais OAuth
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.fuso_horario = "America/Sao_Paulo"
        self.credentials = None
        self.service = None
        
        # Inicializar autenticação
        self._autenticar()
    
    def _autenticar(self):
        """Gerencia o processo de autenticação com persistência de token"""
        # Escopo de acesso ao calendário
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # Verificar se já existe um token salvo
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # Se não há credenciais válidas, solicitar nova autenticação
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # Renovar token expirado
                self.credentials.refresh(Request())
            else:
                # Criar novo fluxo de autenticação
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.credentials = flow.run_local_server(port=8080)
            
            # Salvar as credenciais para uso futuro
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Construir o serviço
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def adicionar_evento(self, titulo, inicio, fim, descricao="", local="", cor=None, fuso_horario=None):
        """
        Adiciona um evento ao calendário com suporte a metadados adicionais.
        
        Args:
            titulo: Título do evento
            inicio: Data/hora de início (formato ISO)
            fim: Data/hora de término (formato ISO)
            descricao: Descrição detalhada do evento
            local: Localização do evento
            cor: ID da cor do evento (1-11)
            fuso_horario: Fuso horário (padrão: America/Sao_Paulo)
            
        Returns:
            ID do evento criado
        """
        if fuso_horario is None:
            fuso_horario = self.fuso_horario
            
        # Preparar corpo do evento
        evento = {
            'summary': titulo,
            'start': {'dateTime': inicio, 'timeZone': fuso_horario},
            'end': {'dateTime': fim, 'timeZone': fuso_horario}
        }
        
        # Adicionar campos opcionais se fornecidos
        if descricao:
            evento['description'] = descricao
        if local:
            evento['location'] = local
        if cor:
            evento['colorId'] = cor
            
        # Criar evento e retornar ID
        resultado = self.service.events().insert(
            calendarId='primary',
            body=evento
        ).execute()
        
        return resultado.get('id')
    
    def listar_eventos(self, inicio=None, fim=None, max_resultados=10, query=None):
        """
        Lista eventos do calendário com suporte a filtros avançados.
        
        Args:
            inicio: Data/hora de início para filtro (formato ISO)
            fim: Data/hora de término para filtro (formato ISO)
            max_resultados: Número máximo de resultados
            query: Texto para busca em eventos
            
        Returns:
            Lista de eventos
        """
        # Se não for especificado, usar data/hora atual
        if inicio is None:
            inicio = datetime.now(pytz.timezone(self.fuso_horario)).isoformat()
            
        # Preparar parâmetros da consulta
        params = {
            'calendarId': 'primary',
            'timeMin': inicio,
            'maxResults': max_resultados,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        # Adicionar parâmetros opcionais
        if fim:
            params['timeMax'] = fim
        if query:
            params['q'] = query
            
        # Executar consulta
        eventos = self.service.events().list(**params).execute()
        return eventos.get('items', [])
    
    def obter_evento(self, evento_id):
        """
        Obtém detalhes de um evento específico pelo ID.
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Detalhes do evento ou None se não encontrado
        """
        try:
            return self.service.events().get(
                calendarId='primary',
                eventId=evento_id
            ).execute()
        except Exception:
            return None
    
    def atualizar_evento(self, evento_id, dados):
        """
        Atualiza um evento existente.
        
        Args:
            evento_id: ID do evento a ser atualizado
            dados: Dicionário com os campos a serem atualizados
            
        Returns:
            Evento atualizado ou None em caso de erro
        """
        try:
            # Obter evento atual
            evento = self.service.events().get(
                calendarId='primary',
                eventId=evento_id
            ).execute()
            
            # Atualizar campos
            for chave, valor in dados.items():
                evento[chave] = valor
                
            # Enviar atualização
            return self.service.events().update(
                calendarId='primary',
                eventId=evento_id,
                body=evento
            ).execute()
        except Exception as e:
            print(f"Erro ao atualizar evento: {str(e)}")
            return None
    
    def excluir_evento(self, evento_id):
        """
        Exclui um evento do calendário.
        
        Args:
            evento_id: ID do evento a ser excluído
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=evento_id
            ).execute()
            return True
        except Exception:
            return False
    
    def buscar_horarios_livres(self, data_inicio, data_fim, duracao_minutos=60):
        """
        Busca horários livres em um intervalo de datas.
        
        Args:
            data_inicio: Data inicial (formato ISO)
            data_fim: Data final (formato ISO)
            duracao_minutos: Duração mínima do slot livre em minutos
            
        Returns:
            Lista de slots livres no formato {inicio, fim}
        """
        # Obter eventos no período
        eventos = self.listar_eventos(
            inicio=data_inicio,
            fim=data_fim,
            max_resultados=100
        )
        
        # Converter para datetime
        inicio_periodo = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
        fim_periodo = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
        
        # Extrair períodos ocupados
        periodos_ocupados = []
        for evento in eventos:
            inicio_evento = datetime.fromisoformat(
                evento['start']['dateTime'].replace('Z', '+00:00')
            )
            fim_evento = datetime.fromisoformat(
                evento['end']['dateTime'].replace('Z', '+00:00')
            )
            periodos_ocupados.append((inicio_evento, fim_evento))
        
        # Ordenar períodos ocupados
        periodos_ocupados.sort(key=lambda x: x[0])
        
        # Encontrar slots livres
        slots_livres = []
        hora_atual = inicio_periodo
        
        for inicio_ocupado, fim_ocupado in periodos_ocupados:
            # Verificar se há espaço antes do próximo evento
            if (inicio_ocupado - hora_atual).total_seconds() >= duracao_minutos * 60:
                slots_livres.append({
                    'inicio': hora_atual,
                    'fim': hora_atual + timedelta(minutes=duracao_minutos)
                })
            
            # Avançar para depois do evento ocupado
            hora_atual = max(hora_atual, fim_ocupado)
        
        # Verificar se há espaço após o último evento
        if (fim_periodo - hora_atual).total_seconds() >= duracao_minutos * 60:
            slots_livres.append({
                'inicio': hora_atual,
                'fim': hora_atual + timedelta(minutes=duracao_minutos)
            })
        
        return slots_livres
    
    def configurar_lembrete(self, evento_id, minutos_antes=30):
        """
        Configura um lembrete para um evento.
        
        Args:
            evento_id: ID do evento
            minutos_antes: Minutos antes do evento para enviar o lembrete
            
        Returns:
            True se configurado com sucesso, False caso contrário
        """
        try:
            # Obter evento atual
            evento = self.service.events().get(
                calendarId='primary',
                eventId=evento_id
            ).execute()
            
            # Configurar lembrete
            evento['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': minutos_antes},
                    {'method': 'popup', 'minutes': minutos_antes}
                ]
            }
            
            # Atualizar evento
            self.service.events().update(
                calendarId='primary',
                eventId=evento_id,
                body=evento
            ).execute()
            
            return True
        except Exception:
            return False
    
    def obter_cores_disponiveis(self):
        """
        Obtém a lista de cores disponíveis para eventos.
        
        Returns:
            Dicionário com cores disponíveis
        """
        return self.service.colors().get().execute().get('event', {})