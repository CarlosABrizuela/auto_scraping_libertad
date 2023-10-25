from utility_functions import get_config, get_categories
from Scraper import Scraper
import concurrent.futures
from files.sucursales import BRANCHES

def run_scraper(branch, categories, config):
    """Ejecuta el scraper para cada sucursal. creando una instancia en el thread actual.

    Args:
        branch (dict): sucursal. con nombre y código
        categories (list): lista de las categorias
        config (dict): configuración del scraper
        console (Loggin): _imprime por consola
    """
    scraper = Scraper(config)
    scraper.process_branch(branch, categories)

def main():
    """Obtiene la lista de categorias, la configuración del scraper y comienza la extracción de la información
    """
    config = get_config()
    categories = get_categories(config['categories_url'], config)
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['thread_number']) as executor:
        for branch in BRANCHES: 
            executor.submit(run_scraper, branch, categories, config)

if __name__ == "__main__":
    print("Iniciando..")
    main()
    print("Fin")