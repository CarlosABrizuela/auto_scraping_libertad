from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

class Scraper:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()

    def create_csv(self):
        pass

    def process_product(self):
        pass

    def process_category(self):
        pass

    def run(self, url):
        print('main runing...')
        self.driver.get(url)
        sleep(5)
        script_element= self.driver.find_element(By.XPATH, '//script[@type="application/ld+json"]')
        print(script_element.get_attribute("innerHTML"))

