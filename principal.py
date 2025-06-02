import logging
import argparse
import os
import sys
import datetime
import colorama
from colorama import Fore, Style
from commands.gerenciador_tarefas import GerenciadorTarefas
from utils.calendario.google import GerenciadorCalendarioGoogle


# Inicializar colorama para formatação de cores no terminal
colorama.init()

# Configuração de logging melhorada
def configurar_logging():
    """Configura o sistema de logging com rotação de arquivos"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    
    # Criar diretório de logs se não existir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nome do arquivo de log com data
    data_atual = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'assistente_{data_atual}.log')
    
    # Configurar logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    
    # Adicionar handler para console também
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    return log_file

def formatar_evento(evento, detalhado=False):
    """Formata um evento para exibição no terminal com cores"""
    # Extrair informações básicas
    titulo = evento.get('summary', 'Sem título')
    
    # Determinar cor com base na categoria (colorId)
    cor_id = evento.get('colorId', '0')
    cores = {
        '11': Fore.RED,      # Vermelho (trabalho)
        '9': Fore.GREEN,     # Verde (pessoal)
        '7': Fore.BLUE,      # Azul (estudo)
        '5': Fore.YELLOW,    # Amarelo (geral)
        '0': Fore.WHITE      # Branco (padrão)
    }
    cor = cores.get(cor_id, Fore.WHITE)
    
    # Extrair e formatar data/hora
    try:
        data_hora_str = evento['start'].get('dateTime', evento['start'].get('date', ''))
        if 'T' in data_hora_str:
            # Formato com hora (2023-05-28T14:00:00+00:00)
            data_hora = datetime.datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
            data_formatada = data_hora.strftime('%d/%m/%Y %H:%M')
        else:
            # Formato só com data (2023-05-28)
            data_formatada = datetime.datetime.strptime(data_hora_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        data_formatada = "Data desconhecida"
    
    # Formatação básica
    resultado = f"{cor}{titulo}{Style.RESET_ALL} ({data_formatada})"
    
    # Formatação detalhada
    if detalhado:
        resultado += "\n"
        if evento.get('location'):
            resultado += f"  Local: {evento.get('location')}\n"
        if evento.get('description'):
            resultado += f"  Descrição: {evento.get('description')}\n"
        resultado += f"  ID: {evento.get('id', 'Desconhecido')}"
    
    return resultado

def exibir_ajuda():
    """Exibe a ajuda detalhada do assistente"""
    ajuda = f"""
{Fore.CYAN}=== Assistente Virtual de Tarefas - Ajuda ==={Style.RESET_ALL}

{Fore.YELLOW}Comandos Básicos:{Style.RESET_ALL}

{Fore.GREEN}1. Adicionar tarefas:{Style.RESET_ALL}
   - adicionar [descrição da tarefa] [data] [hora]
   Exemplo: adicionar reunião com equipe amanhã às 14h

{Fore.GREEN}2. Criar lembretes:{Style.RESET_ALL}
   - lembrar de [descrição] [data] [hora]
   Exemplo: lembrar de enviar relatório sexta-feira

{Fore.GREEN}3. Listar tarefas:{Style.RESET_ALL}
   - listar tarefas [filtros opcionais]
   Exemplo: listar tarefas da categoria trabalho

{Fore.GREEN}4. Atualizar tarefas:{Style.RESET_ALL}
   - atualizar tarefa id:[ID] [novos dados]
   Exemplo: atualizar tarefa id:abc123 nova descrição amanhã às 10h

{Fore.GREEN}5. Excluir tarefas:{Style.RESET_ALL}
   - excluir tarefa id:[ID]
   Exemplo: excluir tarefa id:abc123

{Fore.GREEN}6. Agendar reuniões:{Style.RESET_ALL}
   - agendar reunião [descrição] [data] [hora] [local opcional]
   Exemplo: agendar reunião com cliente dia 10/06 às 15h na sala 3

{Fore.YELLOW}Parâmetros adicionais:{Style.RESET_ALL}
- categoria:[trabalho|pessoal|estudo|geral]
- prioridade:[alta|média|baixa|normal]
- local:[localização]

{Fore.YELLOW}Comandos do sistema:{Style.RESET_ALL}
- ajuda: Exibe esta mensagem de ajuda
- limpar: Limpa a tela do terminal
- sair: Encerra o assistente

{Fore.YELLOW}Dicas:{Style.RESET_ALL}
- Use linguagem natural para datas: "amanhã", "próxima semana"
- Horários podem ser especificados como "14h", "14:30", "2 da tarde"
- Para tarefas sem horário específico, omita o horário
"""
    print(ajuda)

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_banner():
    """Exibe o banner de boas-vindas do assistente"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║  {Fore.YELLOW}Assistente Virtual Pessoal para Gerenciamento de Tarefas{Fore.CYAN}  ║
║                                                      ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}

Digite {Fore.GREEN}'ajuda'{Style.RESET_ALL} para ver a lista de comandos disponíveis
Digite {Fore.GREEN}'sair'{Style.RESET_ALL} para encerrar o assistente
"""
    print(banner)

def main():
    """Função principal do assistente"""
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Assistente Virtual de Tarefas')
    parser.add_argument('--gui', action='store_true', help='Iniciar com interface gráfica')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso (mais detalhes)')
    args = parser.parse_args()
    
    # Configurar logging
    log_file = configurar_logging()
    logging.info("Iniciando Assistente Virtual de Tarefas")
    
    # Verificar se deve iniciar com GUI
    if args.gui:
        try:
            from interface_grafica import AssistenteGUI
            logging.info("Iniciando interface gráfica")
            app = AssistenteGUI()
            app.executar()
            return
        except ImportError as e:
            logging.error(f"Erro ao carregar interface gráfica: {str(e)}")
            print(f"{Fore.RED}Erro ao carregar interface gráfica. Iniciando modo de linha de comando.{Style.RESET_ALL}")
    
    # Inicializar gerenciador
    try:
        gerenciador = GerenciadorTarefas()
        logging.info("Gerenciador de tarefas inicializado com sucesso")
    except Exception as e:
        logging.critical(f"Erro ao inicializar gerenciador: {str(e)}")
        print(f"{Fore.RED}Erro crítico ao inicializar o assistente: {str(e)}{Style.RESET_ALL}")
        print(f"Verifique o arquivo de log: {log_file}")
        return
    
    # Exibir banner de boas-vindas
    limpar_tela()
    exibir_banner()
    
    # Loop principal
    while True:
        try:
            # Prompt colorido
            comando = input(f"{Fore.CYAN}> {Style.RESET_ALL}")
            comando = comando.strip()
            
            # Ignorar comandos vazios
            if not comando:
                continue
            
            # Processar comandos do sistema
            comando_lower = comando.lower()
            
            if comando_lower == "sair":
                print(f"{Fore.YELLOW}Encerrando assistente...{Style.RESET_ALL}")
                logging.info("Assistente encerrado pelo usuário")
                break
                
            elif comando_lower == "ajuda":
                exibir_ajuda()
                continue
                
            elif comando_lower == "limpar":
                limpar_tela()
                exibir_banner()
                continue
                
            # Processar comandos de listagem
            elif comando_lower.startswith("listar"):
                logging.info(f"Executando comando: {comando}")
                
                # Determinar parâmetros de listagem
                filtro_categoria = None
                filtro_prioridade = None
                
                if "categoria:" in comando_lower:
                    # Extrair categoria do comando
                    partes = comando_lower.split("categoria:")
                    if len(partes) > 1:
                        filtro_categoria = partes[1].split()[0]
                
                if "prioridade:" in comando_lower:
                    # Extrair prioridade do comando
                    partes = comando_lower.split("prioridade:")
                    if len(partes) > 1:
                        filtro_prioridade = partes[1].split()[0]
                
                # Listar eventos com filtros
                eventos = gerenciador.calendario.listar_eventos(max_resultados=20)
                
                # Aplicar filtros manuais se necessário
                if filtro_categoria or filtro_prioridade:
                    eventos_filtrados = []
                    for evento in eventos:
                        # Filtrar por categoria (via colorId)
                        if filtro_categoria:
                            categorias_cores = {
                                "trabalho": "11",
                                "pessoal": "9",
                                "estudo": "7",
                                "geral": "5"
                            }
                            cor_filtro = categorias_cores.get(filtro_categoria)
                            if cor_filtro and evento.get('colorId') != cor_filtro:
                                continue
                        
                        # Filtrar por prioridade (via prefixo no título)
                        if filtro_prioridade:
                            titulo = evento.get('summary', '')
                            if filtro_prioridade == "alta" and not titulo.startswith("⚠️"):
                                continue
                            elif filtro_prioridade == "média" and not titulo.startswith("⚡"):
                                continue
                            elif filtro_prioridade == "baixa" and not titulo.startswith("🔹"):
                                continue
                        
                        eventos_filtrados.append(evento)
                    
                    eventos = eventos_filtrados
                
                # Exibir resultados
                if not eventos:
                    print(f"{Fore.GREEN}✓ Nenhum evento encontrado{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.CYAN}=== Eventos Encontrados ({len(eventos)}) ==={Style.RESET_ALL}")
                    for i, evento in enumerate(eventos, 1):
                        print(f"{i}. {formatar_evento(evento, args.verbose)}")
                    print()
                
            # Processar outros comandos via gerenciador
            else:
                logging.info(f"Executando comando: {comando}")
                resposta = gerenciador.executar_comando(comando)
                print(f"\n{resposta}\n")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operação cancelada pelo usuário{Style.RESET_ALL}")
            continue
            
        except Exception as e:
            logging.error(f"Erro no comando '{comando}': {str(e)}")
            print(f"{Fore.RED}⚠️ Ocorreu um erro: {str(e)}{Style.RESET_ALL}")
            print(f"Verifique o arquivo de log: {log_file}")

if __name__ == "__main__":
    main()