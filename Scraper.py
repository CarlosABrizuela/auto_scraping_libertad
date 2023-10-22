from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import json

import pprint
class Scraper:
    def __init__(self) -> None:
        # Inicializa el navegador
        chrome_options= Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--log-level=3')  # 3: SIN REGISTROS; 
        self.driver = webdriver.Chrome(options=chrome_options)

    def create_csv(self):
        pass

    def process_product(self, grid_productos, item_list_element):
        try:
            product_list = []
            grid_items_productos= self.find_elements(grid_productos, By.XPATH, './div') # obtenemos cada elemento del grid
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
                precio_regular= self.find_element(grid_item_producto, By.CLASS_NAME,'vtex-product-price-1-x-listPrice')
                if precio_regular:
                    dict_prod['precio_regular']= str(precio_regular.text).replace('$ ', '').replace('.', '').replace(',','.') # quitamos el '$ ' al precio
                else:
                    dict_prod['precio_regular']= producto['offers']['offers'][0]['price']

                product_list.append(dict_prod)
                
        except Exception as e:
            print(f'Hubo un error: {e}')
        
        # return product_list
        pprint.pprint(product_list)

    def process_category(self):
        pass

    def run(self, url):
        print('main runing...')
        self.driver.get(url)
        sleep(2)
        item_list_element= None
        script_elements= self.find_elements(self.driver, By.XPATH, '//script[@type="application/ld+json"]')
        for script_element in script_elements:
            dict_script_element = json.loads(script_element.get_attribute('innerHTML'))
            if dict_script_element['@type'] == "ItemList":
                item_list_element= dict_script_element['itemListElement']

        grid_productos= self.find_element(self.driver,By.ID, 'gallery-layout-container')

        self.process_product(grid_productos, item_list_element)
    
    def find_element(self, elemento,  by, value):
        """parameters: 
                elemento: puede ser driver o el elemento para buscar dentro de su html
                by: By.CLASS, By.ID
                value: nombre de la clase, nombre del id.
        """
        try:
            return elemento.find_element(by, value) #elemento puede ser driver
        except NoSuchElementException:
            print(f"No se encontro el elemento:'{value}'")
            return False
    
    def find_elements(self, elemento,  by, value):
        """parameters: 
                elemento: puede ser driver o el elemento para buscar dentro de su html
                by: By.CLASS, By.ID
                value: nombre de la clase, nombre del id.
        """
        try:
            return elemento.find_elements(by, value) #elemento puede ser driver
        except NoSuchElementException:
            print(f"No se encontro el elemento: ({by})'{value}'")
            return False