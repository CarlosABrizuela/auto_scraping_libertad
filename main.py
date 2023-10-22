
from Scraper import Scraper


def main():
    scraper = Scraper()
    url = 'https://www.hiperlibertad.com.ar/tecnologia/celulares-y-tablets/celulares?sc=2'
    scraper.run(url)

if __name__ == "__main__":
    main()