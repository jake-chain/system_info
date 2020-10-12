import os
import subprocess
import time
from django.http import HttpResponse
from django.shortcuts import render

categories = ['handle', 'port connector', 'system slot', 'management device', 'onboard', 'memory', 'cache', 'temperature', 'oem', 'bios', 'processor', 'system', 'chassi']


def home(request) -> HttpResponse:
    """
    Retorna a renderização da visualização da página com as informações do sistema
    :param request:
    :return: render
    """
    return render(request, 'app.html', {
        'data_file': read_system_info(),
        'categories': categories
    })


def read_system_info() -> dict:
    """
    Consulta as informalções do sistema utilizando as funções de execute_subprocess
    Após isso realiza a decodificação do processo para o formato de str usando a função decode_stdout
    :return: Um dict contendo as informações do sistema já agrupados por níveis
    """

    # Consultando as informações do sistema e jpa convertendo para str
    system_info = decode_stdout(execute_subprocess())
    # Caso o retorna da chamada acima for None, ocorreu falha na consulta das informações, então é retornado um dict vazio
    if system_info is None:
        return {}

    # Variável que irá armazenar as informações do sistema em formato de dict
    data_file = {}

    level_01_id = 1
    level_02_id = 1
    level_03_id = 1

    # Percorrendo cada linha do retorna da execução do comando para capturar as informações do sistema e agrupar por níveis em um dict
    for line in system_info.split('\n'):
        # Removendo os recuos para obter apenas o texto
        text = line.replace('	', '').replace('\n', '')
        # Verificando se o texto não está vazio, nesse caso, a linha era apenas um separador
        if text != '':
            # Capturando o nível de recuo da linha para o agrupamento
            level = check_level(line)

            if level == 1:
                data_file[f"{level_01_id}"] = {
                    'text': text,
                    'sub_level_id': None,
                    'category': get_category(text)
                }
                level_01_id += 1
                level_02_id = 1
                level_03_id = 1
            elif level == 2:
                data_file[f"{level_01_id}-{level_02_id}"] = {
                    'text': text,
                    'sub_level_id': level_01_id - 1,
                    'offset': 1
                }
                level_02_id += 1
                level_03_id = 1
            elif level == 3:
                data_file[f"{level_01_id}-{level_02_id}-{level_03_id}"] = {
                    'text': text,
                    'sub_level_id': level_01_id - 1,
                    'offset': 2
                }
                level_03_id += 1
    # Retorno da função
    return data_file


def decode_stdout(executed: subprocess.CompletedProcess or None) -> str or None:
    """
    Nessa função é convertido o retorno de uma execução do subprocess para o formato str de acordo com o sistema operacional atual
    :param executed: Uma instância de CompletedProcess
    :return: str com as informações da execução do processo ou um None em caso de falha
    """

    # Verifica se o parâmetro de entrada não está vazio
    if executed is not None:
        # Verificando qual é o sistema operacional atual para realizar a devida conversão
        if get_system() == 'W':
            # Conversão para o Windows
            return executed.stdout.decode('ISO-8859-1') if executed.returncode == 0 else None
        else:
            # Conversão para os sistema baseados no Linux
            return executed.stdout.decode('UTF-8') if executed.returncode == 0 else None
    else:
        return None


def execute_subprocess() -> subprocess.CompletedProcess or None:
    """
    Função para executar um comando no terminal utilizando a biblioteca do subprocess para captura do retorno
    A função em questão é uma consulta das informações do sistemas
    :return: CompletedProcess A instância da execução do comando
    """

    try:
        # Verificando qual o sistema operacional atual para executar o devido comando
        if get_system() == 'W':
            return subprocess.run(['systeminfo'], stdout=subprocess.PIPE, shell=True)
        else:
            return subprocess.run(['sudo', 'dmidecode', '-', 'TYPE17'], stdout=subprocess.PIPE)
    except Exception as e:
        return get_error(e)


def get_system() -> str:
    """
    Verifica qual o sistema operacional e retorna um caractere específico referente ao S.O
    :return: 'W' para Windows e 'L' para Linux
    """
    return 'W' if os.name == 'nt' else 'L'


def get_category(text: str) -> str:
    """
    Nessa função, é identificado a que categoria a informação do sistema pertence
    :param text: informação a ser vategorizada
    :return: str O código da categoria
    """

    # Converte o texto para letras minúsculas
    text = text.lower()
    # Percorre as categorias pre definidas
    for category in categories:
        # Verifica se a categoria está contida no texto
        if category in text:
            # Retorna a categoria encontrada
            return 'category-' + category.replace(' ', '-')
    # Caso não encontre nenhuma categoria relacionada, retorna 'outros'
    return 'category-others'


def check_level(line) -> int:
    """
    Retorna o nível de espaçamento para a linha do resultado do comando executado no terminal
    Essa função é executada de maneira recursiva
    :param line: Linha lida no terminal
    :return: int Um valor inteiro contendo a quantidade de espaçamento (tabs) de recuo
    """

    # Verificando se existe um recuo na linha
    if '	' in line:
        # Caso tenha, remove esse recuo e chama a função novamente retorna 1 + o retorno da função que pode chegar a n^inifnity
        return 1 + check_level(line.replace('	', '', 1))
    else:
        # Caso não tenha mais recuo, retorna apenas 1, ou seja, sem recuo
        return 1


def get_error(erro) -> None:
    """
    Função para captura de tratamento de exceções e escrita do erro no arquivo
    :param erro: Excption
    :return: None
    """

    # Abrindo o arquivo para escrita
    file_log = open_file('logs', 'a')
    # Escrevendo o erro ocrorrido no arquivo
    file_log.write("Hora: " + time.strftime("%H:%M:%S") + "\nError: " + str(erro) + "\n\n")
    # Fechando o arquivo
    file_log.close()


def open_file(file, method):
    """
    Apenas abre um determinado arquivo em um determinado mode de leitura
    :param file: Arquivo a ser aberto
    :param method: Modo de leitura
    :return: IO instância do arquivo
    """
    return open(get_path(file), method)


def get_path(file="") -> str:
    """
    Retorna o caminho do arquivo de maneira dinâmica
    :param file: Nome do arquivo
    :return: std O caminho completo do arquivo
    """
    return os.path.abspath(file)
