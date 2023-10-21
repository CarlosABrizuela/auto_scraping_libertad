
from Scraper import Scraper


def main():
    scraper = Scraper()
    url = 'https://www.hiperlibertad.com.ar/tecnologia/tv-y-video/tv-led-y-smart-tv?sc=1'
    scraper.run(url)

if __name__ == "__main__":
    main()