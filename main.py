from utility_functions import get_config, get_categories
from Scraper import Scraper


def main():
    config = get_config()
    scraper = Scraper(config)
    categories = get_categories(config['categories_url'])
    scraper.run(categories)

if __name__ == "__main__":
    print("Iniciando..")
    main()
    print("Fin")