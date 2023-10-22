from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json

import pprint
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

        grid_productos= self.driver.find_element(By.ID, 'gallery-layout-container')
        grid_items_productos= grid_productos.find_elements( By.XPATH, './div') # obtenemos cada elemento del grid
        product_list = []
        for item_element, grid_item_producto in zip(item_list_element, grid_items_productos): 
            # iterar los elementos del grid y del json al mismo tiempo (el json no tiene el precio de lista o tachado)
            producto= item_element['item']
            dict_prod= {
            'nombre': producto['name'],
            'precio_publicado': producto['offers']['offers'][0]['price'],
            'categoria': "CATEGORIA",
            'SKU': producto['sku'],
            'url_producto': producto['@id'],
            'stock': producto['offers']['offers'][0]['availability'],
            'descripcion': str(producto['description']).replace('\n', ' ').replace('\r', '') # quitamos los espacios
            }
            try:
                precio_regular= grid_item_producto.find_element(By.CLASS_NAME,'vtex-product-price-1-x-listPrice')
                dict_prod['precio_regular']= str(precio_regular.text).replace('$ ', '').replace('.', '').replace(',','.') # quitamos el '$ ' al precio
            except NoSuchElementException:
                dict_prod['precio_regular']= producto['offers']['offers'][0]['price']

            product_list.append(dict_prod)
        
        pprint.pprint(f'Salida {product_list}')