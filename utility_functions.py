import json
import yaml 
import requests
from requests.exceptions import ProxyError
import logging

def get_config():
    """
    Obtiene los datos de configuracion del archivo /config.yml
    """
    try:
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError as e:
        print(f"El archivo no se encontró. {e.filename}")
        config = {}
        config['proxy'] = False
        config['proxy_ip_port'] = None
        config['output_dir'] = ''
        config['thread_number']= 1
        config['max_attempts']= 0
        config['delay_attempts']= 1
        config['timeout'] = 5
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
    with open("categorias_local.json", 'r', encoding='utf-8') as file:
        return process_list_categories(json.load(file))
        
def init_logging():
    console = logging.getLogger("console_logger")
    console.setLevel(logging.DEBUG)  
    console_handler = logging.StreamHandler() 
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    console.addHandler(console_handler)
    return console
