import json
from pickle import NONE
import yaml 
import requests
from requests.exceptions import ProxyError
import logging
import os
from datetime import datetime

main_dir = os.path.dirname(__file__)
def get_config():
    """
    Obtiene los datos de configuracion del archivo /config.yml
    """
    try:
        file_path = os.path.join(main_dir, 'files', 'config.yaml')
        with open(file_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError as e:
        print(f"El archivo no se encontró. {e.filename}")
        config = {}
        config['proxy']= False
        config['proxy_ip_port']= None
        config['output_dir']= ''
        config['thread_number']= 5
        config['max_attempts']= 0
        config['delay_attempts']= 1
        config['timeout']= 5
        return config

def get_categories(url, config): 
    """Retorna una lista de diccionarios con las categorias y el nombre de la categoria
    Args:
        url (str): la url con el json de las categorias

    Returns:
        list: lista de las categorias
        [{'nombre': , 'url': }, ...]
    """
    if config['proxy']:
        session.proxies = config['proxy_ip_port']

    with requests.session() as session:
        try:
            response =  session.get(url)
            if response.ok:
                return process_list_categories(response.json())
            else:
                print(response.status_code)
                return False
        except ProxyError as e:
            print('(get categories) Error de proxy:', e)
        except requests.RequestException as e:
            print(f"(get categories) Error de solicitud: {e}.")
    return get_local_categories()

def process_list_categories(categorias_json):
    lista_sup= []
    for category in categorias_json:
        if category["hasChildren"]:
            lista_sub= []
            for child in category['children']:
                categoria_dict = {
                    "nombre": child['name'],
                    "url": child["url"]
                }
                lista_sub.append(categoria_dict)

            categoria_dict_sup ={
                "nombre": category['name'],
                "sub_categorias": lista_sub
            }
        lista_sup.append(categoria_dict_sup)
        
    return lista_sup

def get_local_categories():
    # Si no puede acceder al json online. abre el local
    file_path = os.path.join(main_dir, 'files', 'categorias_local.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        return process_list_categories(json.load(file))


# # Dos niveles de loggin. por consola y reporte a un fichero
CONSOLE = logging.getLogger("console_logger")
CONSOLE.setLevel(logging.DEBUG)  
console_handler = logging.StreamHandler() 
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
CONSOLE.addHandler(console_handler)
#
date = datetime.today().strftime('%d-%m-%Y_%H-%M-%S')
file_path = os.path.join(main_dir, 'log', f'{date}_log.txt')
LOG = logging.getLogger("hiper_libertad")
LOG.setLevel(logging.INFO)  
file_handler = logging.FileHandler(file_path)  
file_formatter = logging.Formatter("%(asctime)s - %(name)s | %(levelname)s: %(message)s") 
file_handler.setFormatter(file_formatter)
LOG.addHandler(file_handler)
