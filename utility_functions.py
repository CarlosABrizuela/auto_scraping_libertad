import yaml 
import requests

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
    
categorias =[] 
def get_categories(url):
    """Retorna una lista de diccionarios con las categorias y el nombre de la categoria

    Args:
        url (str): la url con el json de las categorias

    Returns:
        list: lista de las categorias
        [{'nombre': , 'url': }, ...]
    """
    response =  requests.get(url)
    if response.ok:
        get_item_category(response.json())
        return categorias
    else:
        print(response.status_code)
        return False

def get_item_category(categorias_json):
    # Devuelve las categorias hojas, o esas que no tienen categorias hijas.
    for index, categoria in enumerate(categorias_json):
        if categoria["hasChildren"]:
            get_item_category(categoria["children"])
        else:
            categoria_dict = {
                "nombre": categoria["name"],
                "url": categoria["url"]
            }
            categorias.append(categoria_dict)

        if index == len(categorias_json) - 1:
            return
        