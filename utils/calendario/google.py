import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pytz
import pickle

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

class GerenciadorCalendarioGoogle:
    def __init__(self, token_path='token.pickle', credentials_path='credentials.json'):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.fuso_horario = "America/Sao_Paulo"
        self.credentials = None
        self.service = None
        self._autenticar()

    def _autenticar(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.credentials = pickle.load(token)
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.credentials = flow.run_local_server(port=8080)
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.credentials, token)
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def adicionar_evento(self, titulo, inicio, fim, descricao="", local="", cor=None, fuso_horario=None):
        if fuso_horario is None:
            fuso_horario = self.fuso_horario
        evento = {
            'summary': titulo,
            'start': {'dateTime': inicio, 'timeZone': fuso_horario},
            'end': {'dateTime': fim, 'timeZone': fuso_horario}
        }
        if descricao:
            evento['description'] = descricao
        if local:
            evento['location'] = local
        if cor:
            evento['colorId'] = cor

        resultado = self.service.events().insert(calendarId='primary', body=evento).execute()
        return resultado.get('id')

    def listar_eventos(self, inicio=None, fim=None, max_resultados=10, query=None):
        if inicio is None:
            inicio = datetime.now(pytz.timezone(self.fuso_horario)).isoformat()
        params = {
            'calendarId': 'primary',
            'timeMin': inicio,
            'maxResults': max_resultados,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        if fim:
            params['timeMax'] = fim
        if query:
            params['q'] = query
        eventos = self.service.events().list(**params).execute()
        return eventos.get('items', [])

    def obter_evento(self, evento_id):
        try:
            return self.service.events().get(calendarId='primary', eventId=evento_id).execute()
        except Exception:
            return None

    def atualizar_evento(self, evento_id, dados):
        try:
            evento = self.service.events().get(calendarId='primary', eventId=evento_id).execute()
            for chave, valor in dados.items():
                if chave in ['summary', 'description', 'location', 'colorId']:
                    evento[chave] = valor
            return self.service.events().update(calendarId='primary', eventId=evento_id, body=evento).execute()
        except Exception as e:
            print(f"Erro ao atualizar evento: {str(e)}")
            return None

    def excluir_evento(self, evento_id):
        try:
            self.service.events().delete(calendarId='primary', eventId=evento_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao excluir evento: {e}")
            return False

    def buscar_horarios_livres(self, data_inicio, data_fim, duracao_minutos=60):
        try:
            if isinstance(data_inicio, str):
                if data_inicio.endswith("Z"):
                    data_inicio = data_inicio[:-1]
                data_inicio = datetime.fromisoformat(data_inicio)
            if isinstance(data_fim, str):
                if data_fim.endswith("Z"):
                    data_fim = data_fim[:-1]
                data_fim = datetime.fromisoformat(data_fim)

            tz = pytz.timezone(self.fuso_horario)
            inicio_periodo = tz.localize(data_inicio) if data_inicio.tzinfo is None else data_inicio.astimezone(tz)
            fim_periodo = tz.localize(data_fim) if data_fim.tzinfo is None else data_fim.astimezone(tz)

            eventos = self.service.events().list(
                calendarId='primary',
                timeMin=inicio_periodo.isoformat(),
                timeMax=fim_periodo.isoformat(),
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute().get('items', [])

            periodos_ocupados = []
            for evento in eventos:
                if 'dateTime' in evento['start'] and 'dateTime' in evento['end']:
                    inicio = datetime.fromisoformat(evento['start']['dateTime'])
                    fim = datetime.fromisoformat(evento['end']['dateTime'])
                    periodos_ocupados.append((inicio, fim))

            periodos_ocupados.sort(key=lambda x: x[0])
            slots_livres = []
            hora_atual = inicio_periodo

            for inicio_ocupado, fim_ocupado in periodos_ocupados:
                if (inicio_ocupado - hora_atual).total_seconds() >= duracao_minutos * 60:
                    slots_livres.append({
                        'inicio': hora_atual,
                        'fim': hora_atual + timedelta(minutes=duracao_minutos)
                    })
                hora_atual = max(hora_atual, fim_ocupado)

            if (fim_periodo - hora_atual).total_seconds() >= duracao_minutos * 60:
                slots_livres.append({
                    'inicio': hora_atual,
                    'fim': hora_atual + timedelta(minutes=duracao_minutos)
                })

            return slots_livres

        except Exception as e:
            raise Exception(f"Erro ao buscar horários: {str(e)}")

    def configurar_lembrete(self, evento_id, minutos_antes=30):
        try:
            evento = self.service.events().get(calendarId='primary', eventId=evento_id).execute()
            evento['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': minutos_antes},
                    {'method': 'popup', 'minutes': minutos_antes}
                ]
            }
            self.service.events().update(calendarId='primary', eventId=evento_id, body=evento).execute()
            return True
        except Exception:
            return False

    def obter_cores_disponiveis(self):
        return self.service.colors().get().execute().get('event', {})
