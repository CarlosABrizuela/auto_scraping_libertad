from utility_functions import get_config, get_categories, init_logging
from Scraper import Scraper
import concurrent.futures
from sucursales import BRANCHES

def run_scrapper(branch, categories, config, console):
    scraper = Scraper(config, branch, console)
    scraper.process_branch(categories)

def main():
    config = get_config()
    categories = get_categories(config['categories_url'])
    console = init_logging()
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['thread_number']) as executor:
        for branch in BRANCHES: 
            executor.submit(run_scrapper, branch, categories, config, console)

if __name__ == "__main__":
    print("Iniciando..")
    main()
    print("Fin")