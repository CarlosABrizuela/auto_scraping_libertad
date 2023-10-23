from utility_functions import get_config
from Scraper import Scraper


def main():
    config = get_config()
    scraper = Scraper(config)
    url = 'https://www.hiperlibertad.com.ar/tecnologia/celulares-y-tablets/celulares?sc=2'
    scraper.run(url)

if __name__ == "__main__":
    main()