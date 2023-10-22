from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

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
        sleep(2)
        item_list_element= None
        script_elements= self.driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
        for script_element in script_elements:
            dict_script_element = json.loads(script_element.get_attribute('innerHTML'))
            if dict_script_element['@type'] == "ItemList":
                item_list_element= dict_script_element['itemListElement']

        product_list = []
        for item_element in item_list_element: 
            producto= item_element['item']
            print(f'producto: {producto}')
            dict_prod= {
            'nombre': producto['name'],
            'precio_publicado': producto['offers']['offers'][0]['price'],
            'precio_regular': producto['offers']['offers'][0]['price'],
            'categoria': "CATEGORIA",
            'SKU': producto['sku'],
            'url_producto': producto['@id'],
            'stock': producto['offers']['offers'][0]['availability'],
            'descripcion': str(producto['description']).replace('\n', ' ').replace('\r', '') # quitamos los espacios
            }
            product_list.append(dict_prod)
        
        print(f'Salida {product_list}')